import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="PG Rules System", layout="centered")
st.title("🏠 PG Rules System")

role = st.radio("Login as:", ["User", "Admin"])

# ---------------- AUTH ----------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(creds)

PG_DATA_ID = "1y60dTYBKgkOi7J37jtGK4BkkmUoZF8yD4P5J3xA5q6Q"
RULES_ID = "10y6pbBrz-4lXbes4c4vnvJymlZFIDkZujLn1oMZaCaE"

# ---------------- LOAD ----------------
@st.cache_data(ttl=300)
def load_sheet(sheet_id, sheet_name):
    try:
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
        df = pd.DataFrame(sheet.get_all_records())

        if df.empty:
            return pd.DataFrame()

        # clean columns
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

        return df.fillna("")
    except:
        return pd.DataFrame()

# ---------------- PG DATA ----------------
pg_df = load_sheet(PG_DATA_ID, "Sheet1")

if pg_df.empty:
    st.error("PG data missing")
    st.stop()

if "pg_name" not in pg_df.columns:
    st.error("pg_name column missing in PG sheet")
    st.stop()

pg_df["pg_name"] = pg_df["pg_name"].astype(str).str.lower()
pg_names = pg_df["pg_name"].unique().tolist()

# ================= USER =================
if role == "User":

    selected_pg = st.selectbox("Select PG", pg_names)

    rules_df = load_sheet(RULES_ID, "rules")

    if rules_df.empty:
        st.warning("No rules found")
        st.stop()

    rules_df["pg_name"] = rules_df["pg_name"].astype(str).str.lower()

    pg_rows = rules_df[rules_df["pg_name"] == selected_pg]

    if pg_rows.empty:
        st.warning("Rules not added yet")
        st.stop()

    pg = pg_rows.iloc[-1]

    def card(title, content):
        st.markdown(f"""
        <div style="background:white;padding:12px;border-radius:10px;margin-bottom:10px">
        <b>{title}</b><br>{content}
        </div>
        """, unsafe_allow_html=True)

    card("⏰ Freedom",
         f"Curfew: {pg.get('curfew')}<br>Late Entry: {pg.get('late_entry')}<br>Visitors: {pg.get('visitors_time')}")

    card("🍛 Food",
         f"{pg.get('breakfast_time')} / {pg.get('lunch_time')} / {pg.get('dinner_time')}")

    card("📅 Notice",
         f"{pg.get('notice_days')} days<br>{pg.get('notice_policy')}")

    card("🔐 Security",
         f"ID: {pg.get('id_required')}<br>Gate: {pg.get('gate_strict')}")

    card("⚡ Utilities",
         f"Power: {pg.get('power_included')}<br>Maintenance: {pg.get('maintenance_charge')}")

    card("🚫 Restrictions",
         f"Cooking: {pg.get('cooking_allowed')}<br>Music: {pg.get('music_allowed')}")

    card("🔑 Penalties",
         f"Key Loss: {pg.get('key_loss_charge')}<br>Damage: {pg.get('damage_policy')}")

# ================= ADMIN =================
if role == "Admin":

    st.subheader("🛠 Manage PG Rules")

    rules_sheet = client.open_by_key(RULES_ID).worksheet("rules")
    rules_df = load_sheet(RULES_ID, "rules")

    pg_name = st.selectbox("Select PG", pg_names)

    # -------- EXISTING DATA --------
    rules_df["pg_name"] = rules_df["pg_name"].astype(str).str.lower()
    pg_rows = rules_df[rules_df["pg_name"] == pg_name]

    if not pg_rows.empty:
        existing = pg_rows.iloc[-1].to_dict()
        is_new = False
    else:
        existing = {}
        is_new = True

    # ---------- STYLE ----------
    st.markdown("""
    <style>
    input::placeholder, textarea::placeholder {
        color: #999 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ---------- BASIC ----------
    guests_allowed = st.selectbox(
        "Guests Allowed",
        ["Yes","No"],
        index=0 if not is_new and existing.get("guests_allowed")=="Yes" else 1
    )

    cleaning_options = ["Daily","Weekly","Twice Weekly","Thrice Weekly"]

    cleaning = st.selectbox(
        "Cleaning",
        cleaning_options,
        index=0 if is_new else cleaning_options.index(existing.get("cleaning","Daily"))
    )

    # ---------- ENTRY ----------
    curfew = st.text_input(
        "Curfew Time",
        value="" if is_new else existing.get("curfew",""),
        placeholder="e.g. 10:30 PM"
    )

    late_entry = st.selectbox(
        "Late Entry",
        ["No","Yes"],
        index=1 if existing.get("late_entry")=="Yes" else 0
    )

    if guests_allowed == "Yes":
        visitors_time = st.text_input(
            "Visitors Timing",
            value="" if is_new else existing.get("visitors_time",""),
            placeholder="10AM - 6PM"
        )
    else:
        visitors_time = "Not Allowed"

    smoking = st.selectbox(
        "Smoking",
        ["No","Yes"],
        index=1 if existing.get("smoking")=="Yes" else 0
    )

    alcohol = st.selectbox(
        "Alcohol",
        ["No","Yes"],
        index=1 if existing.get("alcohol")=="Yes" else 0
    )

    # ---------- NOTICE ----------
    notice_days = st.number_input(
        "Notice Days",
        value=0 if is_new else int(existing.get("notice_days",0))
    )

    notice_policy = st.text_area(
        "Notice Policy",
        value="" if is_new else existing.get("notice_policy",""),
        placeholder="30 days notice required. Otherwise advance not refundable"
    )

    # ---------- FOOD ----------
    col1, col2, col3 = st.columns(3)

    breakfast_time = col1.text_input("Breakfast", value="" if is_new else existing.get("breakfast_time",""), placeholder="8:00 AM")
    lunch_time = col2.text_input("Lunch", value="" if is_new else existing.get("lunch_time",""), placeholder="1:00 PM")
    dinner_time = col3.text_input("Dinner", value="" if is_new else existing.get("dinner_time",""), placeholder="9:00 PM")

    # ---------- EXTRA ----------
    id_required = st.selectbox("ID Required", ["Yes","No"], index=0 if existing.get("id_required","Yes")=="Yes" else 1)
    gate_strict = st.selectbox("Gate Strict", ["Yes","No"], index=0 if existing.get("gate_strict","Yes")=="Yes" else 1)
    power_included = st.selectbox("Power Included", ["Yes","No"], index=0 if existing.get("power_included","Yes")=="Yes" else 1)

    maintenance_charge = st.text_input("Maintenance", value="" if is_new else existing.get("maintenance_charge",""))

    cooking_allowed = st.selectbox("Cooking Allowed", ["Yes","No"], index=0 if existing.get("cooking_allowed","Yes")=="Yes" else 1)
    music_allowed = st.selectbox("Music Allowed", ["Yes","No"], index=0 if existing.get("music_allowed","Yes")=="Yes" else 1)

    key_loss_charge = st.text_input("Key Loss Charge", value="" if is_new else existing.get("key_loss_charge",""))
    damage_policy = st.text_input("Damage Policy", value="" if is_new else existing.get("damage_policy",""))

    # ---------- SAVE ----------
    if st.button("💾 Save / Update"):

        header = [
            "pg_name","notice_days","notice_policy",
            "breakfast_time","lunch_time","dinner_time",
            "guests_allowed","cleaning","curfew",
            "smoking","alcohol","late_entry","visitors_time",
            "id_required","gate_strict","power_included",
            "maintenance_charge","cooking_allowed","music_allowed",
            "key_loss_charge","damage_policy","timestamp"
        ]

        all_data = rules_sheet.get_all_values()

        new_data = [header] + [
            row for row in all_data[1:]
            if row[0].strip().lower() != pg_name
        ]

        new_data.append([
            pg_name,
            notice_days,
            notice_policy,
            breakfast_time,
            lunch_time,
            dinner_time,
            guests_allowed,
            cleaning,
            curfew,
            smoking,
            alcohol,
            late_entry,
            visitors_time,
            id_required,
            gate_strict,
            power_included,
            maintenance_charge,
            cooking_allowed,
            music_allowed,
            key_loss_charge,
            damage_policy,
            str(datetime.now())
        ])

        rules_sheet.clear()
        rules_sheet.update("A1", new_data)

        st.cache_data.clear()
        st.success("✅ Saved successfully")
        st.rerun()
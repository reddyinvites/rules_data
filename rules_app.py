import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="PG Rules System", layout="centered")
st.title("🏠 PG Rules System")

# ---------------- ROLE ----------------
role = st.radio("Login as:", ["User", "Admin"])

# ---------------- GOOGLE AUTH ----------------
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

# ---------------- CACHE ----------------
@st.cache_data(ttl=300)
def load_sheet(sheet_id, sheet_name):
    try:
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
        df = pd.DataFrame(sheet.get_all_records())
        if df.empty:
            return pd.DataFrame()

        # ✅ CLEAN COLUMN NAMES (IMPORTANT)
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

        return df.fillna("")
    except Exception as e:
        st.error(f"Sheet loading error: {e}")
        return pd.DataFrame()

# ---------------- PG DATA ----------------
pg_df = load_sheet(PG_DATA_ID, "Sheet1")

if pg_df.empty:
    st.error("PG data missing")
    st.stop()

if "pg_name" not in pg_df.columns:
    st.error("❌ 'pg_name' column not found in PG sheet")
    st.stop()

pg_df["pg_name"] = pg_df["pg_name"].astype(str).str.strip().str.lower()
pg_names = pg_df["pg_name"].unique().tolist()

# ================= USER =================
if role == "User":

    selected_pg = st.selectbox("🔍 Select PG", pg_names)

    rules_df = load_sheet(RULES_ID, "rules")

    if rules_df.empty:
        st.warning("No rules found")
        st.stop()

    if "pg_name" not in rules_df.columns:
        st.error("❌ 'pg_name' missing in rules sheet")
        st.stop()

    rules_df["pg_name"] = rules_df["pg_name"].astype(str).str.lower()

    pg_rows = rules_df[rules_df["pg_name"] == selected_pg]

    if pg_rows.empty:
        st.warning("Rules not added yet")
        st.stop()

    pg = pg_rows.iloc[-1]

    # ---------- UI ----------
    def card(title, content):
        st.markdown(f"""
        <div style="background:white;padding:12px;border-radius:10px;margin-bottom:10px">
        <b>{title}</b><br>{content}
        </div>
        """, unsafe_allow_html=True)

    card("⏰ Freedom",
         f"Curfew: {pg.get('curfew')}<br>Late Entry: {pg.get('late_entry')}<br>Visitors: {pg.get('visitors_time')}")

    card("🚭 Lifestyle",
         f"Smoking: {pg.get('smoking')}<br>Alcohol: {pg.get('alcohol')}")

    card("🍛 Food",
         f"Breakfast: {pg.get('breakfast_time')}<br>"
         f"Lunch: {pg.get('lunch_time')}<br>"
         f"Dinner: {pg.get('dinner_time')}")

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

    pg_name = st.selectbox("Select PG", pg_names)

    # ---------- BASIC ----------
    guests_allowed = st.selectbox("Guests Allowed", ["Yes","No"])
    cleaning = st.selectbox("Cleaning", ["Daily","Weekly","Twice Weekly","Thrice Weekly"])

    # ---------- ENTRY ----------
    curfew = st.text_input("Curfew Time")
    late_entry = st.selectbox("Late Entry", ["No","Yes"])

    if guests_allowed == "Yes":
        visitors_time = st.text_input("Visitors Timing")
    else:
        visitors_time = "Not Allowed"

    smoking = st.selectbox("Smoking", ["No","Yes"])
    alcohol = st.selectbox("Alcohol", ["No","Yes"])

    # ---------- NOTICE ----------
    notice_days = st.number_input("Notice Days", 0)
    notice_policy = st.text_area("Notice Policy")

    # ---------- FOOD ----------
    col1,col2,col3 = st.columns(3)
    breakfast_time = col1.text_input("Breakfast")
    lunch_time = col2.text_input("Lunch")
    dinner_time = col3.text_input("Dinner")

    # ---------- EXTRA ----------
    id_required = st.selectbox("ID Required", ["Yes","No"])
    gate_strict = st.selectbox("Gate Strict", ["Yes","No"])
    power_included = st.selectbox("Power Included", ["Yes","No"])
    maintenance_charge = st.text_input("Maintenance")

    cooking_allowed = st.selectbox("Cooking Allowed", ["Yes","No"])
    music_allowed = st.selectbox("Music Allowed", ["Yes","No"])

    key_loss_charge = st.text_input("Key Loss Charge")
    damage_policy = st.text_input("Damage Policy")

    # ---------- SAVE ----------
    if st.button("💾 Save / Update"):

        all_data = rules_sheet.get_all_values()

        header = all_data[0] if all_data else [
            "pg_name","notice_days","notice_policy",
            "breakfast_time","lunch_time","dinner_time",
            "guests_allowed","cleaning","curfew",
            "smoking","alcohol","late_entry","visitors_time",
            "id_required","gate_strict","power_included",
            "maintenance_charge","cooking_allowed","music_allowed",
            "key_loss_charge","damage_policy","timestamp"
        ]

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
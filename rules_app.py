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
    st.error("pg_name column missing")
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
    pg = rules_df[rules_df["pg_name"] == selected_pg].iloc[-1]

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

# ================= ADMIN =================
if role == "Admin":

    st.subheader("🛠 Manage PG Rules")

    rules_sheet = client.open_by_key(RULES_ID).worksheet("rules")
    rules_df = load_sheet(RULES_ID, "rules")

    pg_name = st.selectbox("Select PG", pg_names)

    # -------- LOAD EXISTING --------
    rules_df["pg_name"] = rules_df["pg_name"].astype(str).str.lower()
    pg_rows = rules_df[rules_df["pg_name"] == pg_name]

    existing = pg_rows.iloc[-1].to_dict() if not pg_rows.empty else {}

    # ---------- STYLE ----------
    st.markdown("""
    <style>
    input::placeholder, textarea::placeholder {
        color: gray !important;
        opacity: 0.7;
    }
    </style>
    """, unsafe_allow_html=True)

    # ---------- BASIC ----------
    guests_allowed = st.selectbox(
        "Guests Allowed",
        ["Yes","No"],
        index=0 if existing.get("guests_allowed","Yes")=="Yes" else 1
    )

    cleaning_options = ["Daily","Weekly","Twice Weekly","Thrice Weekly"]
    cleaning = st.selectbox(
        "Cleaning",
        cleaning_options,
        index=cleaning_options.index(existing.get("cleaning","Daily"))
    )

    # ---------- ENTRY ----------
    curfew = st.text_input("Curfew Time",
        value=existing.get("curfew",""),
        placeholder="e.g. 10:30 PM")

    late_entry = st.selectbox(
        "Late Entry",
        ["No","Yes"],
        index=1 if existing.get("late_entry")=="Yes" else 0
    )

    if guests_allowed == "Yes":
        visitors_time = st.text_input(
            "Visitors Timing",
            value=existing.get("visitors_time",""),
            placeholder="e.g. 10AM - 6PM"
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
        value=int(existing.get("notice_days",0))
    )

    notice_policy = st.text_area(
        "Notice Policy",
        value=existing.get("notice_policy",""),
        placeholder="30 days notice required"
    )

    # ---------- FOOD ----------
    col1,col2,col3 = st.columns(3)

    breakfast_time = col1.text_input(
        "Breakfast",
        value=existing.get("breakfast_time",""),
        placeholder="8:00 AM"
    )

    lunch_time = col2.text_input(
        "Lunch",
        value=existing.get("lunch_time",""),
        placeholder="1:00 PM"
    )

    dinner_time = col3.text_input(
        "Dinner",
        value=existing.get("dinner_time",""),
        placeholder="9:00 PM"
    )

    # ---------- SAVE ----------
    if st.button("💾 Save / Update"):

        header = [
            "pg_name","notice_days","notice_policy",
            "breakfast_time","lunch_time","dinner_time",
            "guests_allowed","cleaning","curfew",
            "smoking","alcohol","late_entry","visitors_time",
            "timestamp"
        ]

        new_data = [header]

        for _, row in rules_df.iterrows():
            if row["pg_name"] != pg_name:
                new_data.append(row.tolist())

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
            str(datetime.now())
        ])

        rules_sheet.clear()
        rules_sheet.update("A1", new_data)

        st.cache_data.clear()
        st.success("✅ Saved successfully")
        st.rerun()
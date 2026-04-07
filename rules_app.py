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
        df.columns = [c.strip().lower() for c in df.columns]
        return df.fillna("")
    except:
        return pd.DataFrame()

# ---------------- PG DATA ----------------
pg_df = load_sheet(PG_DATA_ID, "Sheet1")

if pg_df.empty:
    st.error("PG data missing")
    st.stop()

pg_df["pg_name"] = pg_df["pg_name"].str.lower()
pg_names = pg_df["pg_name"].unique().tolist()

# ================= USER =================
if role == "User":

    selected_pg = st.selectbox("🔍 Select PG", pg_names)

    rules_df = load_sheet(RULES_ID, "rules")

    if rules_df.empty:
        st.warning("No rules found")
        st.stop()

    rules_df["pg_name"] = rules_df["pg_name"].str.lower()
    pg_rules = rules_df[rules_df["pg_name"] == selected_pg]

    if pg_rules.empty:
        st.warning("Rules not added yet")
        st.stop()

    pg = pg_rules.iloc[-1]

    st.subheader(f"🏠 {selected_pg.title()}")

    # UI STYLE
    st.markdown("""
    <style>
    .card {background:white;padding:15px;border-radius:12px;
    box-shadow:0 3px 8px rgba(0,0,0,0.08);margin-bottom:10px;}
    .title {font-weight:bold;margin-bottom:6px;}
    .top {background:#eef2f7;padding:12px;border-radius:10px;margin-bottom:10px;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="top">
    ⏰ {pg.get('curfew')} | 🚭 {pg.get('smoking')} | 👥 {pg.get('guests_allowed')}
    </div>
    """, unsafe_allow_html=True)

    def card(title, content):
        st.markdown(f"""
        <div class="card">
        <div class="title">{title}</div>
        {content}
        </div>
        """, unsafe_allow_html=True)

    card("⏰ Freedom",
         f"Curfew: {pg.get('curfew')}<br>Late Entry: {pg.get('late_entry')}<br>Visitors: {pg.get('visitors_time')}")

    card("🚭 Lifestyle",
         f"Smoking: {pg.get('smoking')}<br>Alcohol: {pg.get('alcohol')}")

    card("🧹 Daily Life",
         f"Cleaning: {pg.get('cleaning')}<br>"
         f"Breakfast: {pg.get('breakfast_time')}<br>"
         f"Lunch: {pg.get('lunch_time')}<br>"
         f"Dinner: {pg.get('dinner_time')}")

    card("📅 Notice",
         f"{pg.get('notice_days')} days<br>{pg.get('notice_policy')}")

    st.caption(f"🕒 Last Updated: {pg.get('timestamp','N/A')}")

    agree = st.checkbox("I agree to rules")

    if agree:
        st.success("✅ Ready to proceed")
    else:
        st.warning("⚠️ Accept rules")

# ================= ADMIN =================
if role == "Admin":

    st.subheader("🛠 Manage PG Rules")

    rules_sheet = client.open_by_key(RULES_ID).worksheet("rules")

    pg_name = st.selectbox("Select PG", pg_names)

    # ---------- BASIC ----------
    st.markdown("### 📜 Basic Rules")

    guests_allowed = st.selectbox("Guests Allowed", ["Yes", "No"])

    cleaning = st.selectbox(
        "Cleaning Frequency",
        ["Daily", "Weekly", "Twice Weekly", "Thrice Weekly"]
    )

    # ---------- ADVANCED ----------
    st.markdown("### 🔒 Entry Rules")

    curfew = st.text_input("Curfew Time (Entry closing time)")
    late_entry = st.selectbox("Late Entry Allowed", ["No", "Yes"])

    if guests_allowed == "Yes":
        visitors_time = st.text_input("Visitors Timing (e.g. 10AM - 6PM)")
    else:
        visitors_time = "Not Allowed"

    smoking = st.selectbox("Smoking Allowed", ["No", "Yes"])
    alcohol = st.selectbox("Alcohol Allowed", ["No", "Yes"])

    # ---------- NOTICE ----------
    st.markdown("### 📅 Notice Policy")

    notice_days = st.number_input("Notice Days", 0)

    notice_policy = st.text_area(
        "Notice Description",
        placeholder="30 days notice required. Otherwise advance is not refundable"
    )

    # ---------- FOOD ----------
    st.markdown("### 🍛 Food Timings")

    col1, col2, col3 = st.columns(3)

    breakfast_time = col1.text_input("Breakfast")
    lunch_time = col2.text_input("Lunch")
    dinner_time = col3.text_input("Dinner")

    # ---------- SAVE ----------
    if st.button("💾 Save / Update"):

        all_data = rules_sheet.get_all_values()

        header = all_data[0] if all_data else [
            "pg_name","notice_days","notice_policy",
            "breakfast_time","lunch_time","dinner_time",
            "guests_allowed","cleaning","curfew",
            "smoking","alcohol","late_entry","visitors_time",
            "timestamp"
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
            str(datetime.now())
        ])

        rules_sheet.clear()
        rules_sheet.update("A1", new_data)

        st.cache_data.clear()
        st.success("✅ Rules saved")
        st.rerun()
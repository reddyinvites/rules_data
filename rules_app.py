import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="PG Rules Admin", layout="centered")

st.title("🏠 PG Rules Admin Dashboard")

# ---------------- GOOGLE AUTH ----------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)

client = gspread.authorize(creds)

# ---------------- SHEETS ----------------
PG_DATA_ID = "1y60dTYBKgkOi7J37jtGK4BkkmUoZF8yD4P5J3xA5q6Q"
RULES_ID = "10y6pbBrz-4lXbes4c4vnvJymlZFIDkZujLn1oMZaCaE"

# ---------------- LOAD PG NAMES ----------------
pg_sheet = client.open_by_key(PG_DATA_ID).worksheet("Sheet1")
pg_df = pd.DataFrame(pg_sheet.get_all_records())

pg_df.columns = [str(c).strip().lower() for c in pg_df.columns]

if "pg_name" not in pg_df.columns:
    st.error("❌ pg_data must have 'pg_name'")
    st.stop()

pg_names = pg_df["pg_name"].dropna().unique().tolist()

# ---------------- RULES SHEET ----------------
rules_sheet = client.open_by_key(RULES_ID).worksheet("rules")

# ---------------- FORM ----------------
st.subheader("➕ Add / Update PG Rules")

# ✅ DROPDOWN INSTEAD OF TEXT INPUT
pg_name = st.selectbox("Select PG", pg_names)

st.markdown("### 💰 Money")
rent = st.number_input("Rent", min_value=0)
advance = st.number_input("Advance", min_value=0)
refund_policy = st.text_input("Refund Policy")

st.markdown("### 📅 Notice")
notice_days = st.number_input("Notice Days", min_value=0)

st.markdown("### 📜 Rules")
guests_allowed = st.selectbox("Guests Allowed", ["Yes", "No"])
cleaning = st.selectbox("Cleaning", ["Daily", "Weekly", "Monthly"])

st.markdown("### 🍛 Food Timings")
breakfast_time = st.text_input("Breakfast Time")
dinner_time = st.text_input("Dinner Time")

# ---------------- SAVE ----------------
if st.button("💾 Save Rules"):

    rules_sheet.append_row([
        pg_name.strip().lower(),
        rent,
        advance,
        refund_policy,
        notice_days,
        breakfast_time,
        dinner_time,
        guests_allowed,
        cleaning,
        str(datetime.now())
    ])

    st.success(f"✅ Rules saved for {pg_name}")
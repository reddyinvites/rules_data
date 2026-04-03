import streamlit as st
import gspread
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

SHEET_ID = "10y6pbBrz-4lXbes4c4vnvJymlZFIDkZujLn1oMZaCaE"
sheet = client.open_by_key(SHEET_ID).worksheet("rules")

# ---------------- FORM ----------------
st.subheader("➕ Add / Update PG Rules")

pg_name = st.text_input("PG Name")

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

    if not pg_name:
        st.error("PG Name required")
    else:
        sheet.append_row([
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

        st.success("✅ Rules Saved Successfully!")
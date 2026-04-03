import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="PG Rules System", layout="centered")

st.title("🏠 PG Rules System")

# ---------------- ROLE SWITCH ----------------
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

# ---------------- LOAD PG DATA ----------------
pg_df = pd.DataFrame(
    client.open_by_key(PG_DATA_ID).worksheet("Sheet1").get_all_records()
)

pg_df.columns = [str(c).strip().lower() for c in pg_df.columns]
pg_df = pg_df.fillna("")
pg_df["pg_name"] = pg_df["pg_name"].str.strip().str.lower()

pg_names = pg_df["pg_name"].unique().tolist()

# =========================
# 👤 USER SECTION
# =========================
if role == "User":

    st.subheader("🔍 Select PG")

    selected_pg = st.selectbox("Choose PG", pg_names)

    rules_df = pd.DataFrame(
        client.open_by_key(RULES_ID).worksheet("rules").get_all_records()
    )

    rules_df.columns = [str(c).strip().lower() for c in rules_df.columns]
    rules_df = rules_df.fillna("")
    rules_df["pg_name"] = rules_df["pg_name"].str.strip().str.lower()

    pg_rules = rules_df[rules_df["pg_name"] == selected_pg]

    if pg_rules.empty:
        st.warning("⚠️ No rules found")
        st.stop()

    pg = pg_rules.iloc[-1]

    st.subheader(f"🏠 {selected_pg.title()}")

    st.markdown(f"""
    <div style="background:#FFD84D;padding:20px;border-radius:12px">

    <h3>RULES & REGULATIONS</h3>

    <h4>💰 Money</h4>
    <ul>
    <li>Rent: ₹{pg.get('rent')}</li>
    <li>Advance: ₹{pg.get('advance')}</li>
    <li>Refund: {pg.get('refund_policy')}</li>
    </ul>

    <h4>📅 Notice</h4>
    <ul>
    <li>{pg.get('notice_days')} days</li>
    </ul>

    <h4>📜 Basic Rules</h4>
    <ul>
    <li>Guests: {pg.get('guests_allowed')}</li>
    <li>Cleaning: {pg.get('cleaning')}</li>
    </ul>

    <h4>🔒 Advanced Rules</h4>
    <ul>
    <li>Curfew: {pg.get('curfew')}</li>
    <li>Smoking: {pg.get('smoking')}</li>
    <li>Alcohol: {pg.get('alcohol')}</li>
    <li>Late Entry: {pg.get('late_entry')}</li>
    <li>Visitors: {pg.get('visitors_time')}</li>
    </ul>

    <h4>🏠 Facilities</h4>
    <ul>
    <li>WiFi: {pg.get('wifi')}</li>
    <li>Laundry: {pg.get('laundry')}</li>
    <li>Parking: {pg.get('parking')}</li>
    <li>Power Backup: {pg.get('power_backup')}</li>
    <li>Room Type: {pg.get('room_type')}</li>
    </ul>

    <hr>

    <h4>🍛 FOOD TIMINGS</h4>
    <p>
    Breakfast: {pg.get('breakfast_time')}<br>
    Dinner: {pg.get('dinner_time')}
    </p>

    </div>
    """, unsafe_allow_html=True)

    agree = st.checkbox("I agree to rules")

    if agree:
        st.success("✅ Ready to book")
    else:
        st.warning("⚠️ Accept rules")

# =========================
# 🛠 ADMIN SECTION
# =========================
if role == "Admin":

    st.subheader("➕ Add / Update PG Rules")

    rules_sheet = client.open_by_key(RULES_ID).worksheet("rules")

    pg_name = st.selectbox("Select PG", pg_names)

    st.markdown("### 💰 Money")
    rent = st.number_input("Rent", min_value=0)
    advance = st.number_input("Advance", min_value=0)
    refund_policy = st.text_input("Refund Policy")

    st.markdown("### 📅 Notice")
    notice_days = st.number_input("Notice Days", min_value=0)

    st.markdown("### 📜 Basic Rules")
    guests_allowed = st.selectbox("Guests Allowed", ["Yes", "No"])
    cleaning = st.selectbox("Cleaning", ["Daily", "Weekly", "Monthly"])

    st.markdown("### 🔒 Advanced Rules")
    curfew = st.text_input("Curfew Time")
    smoking = st.selectbox("Smoking Allowed", ["No", "Yes"])
    alcohol = st.selectbox("Alcohol Allowed", ["No", "Yes"])
    late_entry = st.selectbox("Late Entry Allowed", ["No", "Yes"])
    visitors_time = st.text_input("Visitors Timing")

    st.markdown("### 🏠 Facilities")
    wifi = st.selectbox("WiFi", ["Yes", "No"])
    laundry = st.selectbox("Laundry", ["Yes", "No"])
    parking = st.selectbox("Parking", ["Yes", "No"])
    power_backup = st.selectbox("Power Backup", ["Yes", "No"])
    room_type = st.selectbox("Room Type", ["AC", "Non-AC", "Both"])

    st.markdown("### 🍛 Food")
    breakfast_time = st.text_input("Breakfast Time")
    dinner_time = st.text_input("Dinner Time")

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
            curfew,
            smoking,
            alcohol,
            late_entry,
            visitors_time,
            wifi,
            laundry,
            parking,
            power_backup,
            room_type,
            str(datetime.now())
        ])

        st.success(f"✅ Rules saved for {pg_name}")
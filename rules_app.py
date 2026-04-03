import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="PG Rules Combined", layout="centered")

st.title("🏠 No Hidden Rules (2 Sheet Integration)")

# ---------------- GOOGLE CONNECT ----------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)

client = gspread.authorize(creds)

# ---------------- SHEET IDS ----------------
PG_DATA_ID = "PG_DATA_SHEET_ID_HERE"
PG_RULES_ID = "PG_RULES_SHEET_ID_HERE"

# ---------------- LOAD PG DATA ----------------
pg_sheet = client.open_by_key(PG_DATA_ID).worksheet("Sheet1")
pg_data = pd.DataFrame(pg_sheet.get_all_records())

pg_data.columns = pg_data.columns.str.strip().str.lower()

# ---------------- LOAD RULES DATA ----------------
rules_sheet = client.open_by_key(PG_RULES_ID).worksheet("rules")
rules_data = pd.DataFrame(rules_sheet.get_all_records())

rules_data.columns = rules_data.columns.str.strip().str.lower()

# ---------------- SELECT PG ----------------
pg_names = pg_data["pg_name"].dropna().unique().tolist()
selected_pg = st.selectbox("🔍 Select PG", pg_names)

# ---------------- MATCH RULES ----------------
pg_rules = rules_data[rules_data["pg_name"] == selected_pg]

if pg_rules.empty:
    st.error("❌ Rules not found for this PG")
    st.stop()

pg = pg_rules.iloc[0]

# ---------------- UI ----------------
st.subheader(f"🏠 {selected_pg}")

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
<li>{pg.get('notice_days')} days mandatory</li>
</ul>

<h4>📜 Rules</h4>
<ul>
<li>Guests: {pg.get('guests_allowed')}</li>
<li>Cleaning: {pg.get('cleaning')}</li>
</ul>

<hr>

<h4>🍛 FOOD TIMINGS</h4>
<p>
Breakfast: {pg.get('breakfast_time')}<br>
Dinner: {pg.get('dinner_time')}
</p>

</div>
""", unsafe_allow_html=True)

# ---------------- CONFIRM ----------------
agree = st.checkbox("I agree to PG rules")

if agree:
    if st.button("Confirm Booking"):
        st.success("🎉 Booking Confirmed!")
else:
    st.warning("⚠️ Accept rules to continue")
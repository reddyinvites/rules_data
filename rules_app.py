import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.title("🏠 No Hidden Rules")

# ---------------- GOOGLE SHEETS ----------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)

client = gspread.authorize(creds)

SHEET_ID = "1y60dTYBKgkOi7J37jtGK4BkkmUoZF8yD4P5J3xA5q6Q"

sheet = client.open_by_key(SHEET_ID).worksheet("rules")

data = sheet.get_all_records()
df = pd.DataFrame(data)

# ---------------- CLEAN ----------------
df.columns = df.columns.str.strip().str.lower()

# ---------------- PG SELECT ----------------
pg_list = df["pg_id"].astype(str).tolist()
selected_pg = st.selectbox("Select PG", pg_list)

pg = df[df["pg_id"].astype(str) == selected_pg].iloc[0]

# ---------------- UI ----------------
st.subheader(f"🏠 PG ID: {pg['pg_id']}")

st.markdown(f"""
<div style="background:#FFD84D;padding:20px;border-radius:10px">

<h3>RULES & REGULATIONS</h3>

<h4>💰 Money</h4>
<ul>
<li>Rent: ₹{pg.get('rent')}</li>
<li>Advance: ₹{pg.get('advance')}</li>
<li>Refund Policy: {pg.get('refund_policy')}</li>
</ul>

<h4>📅 Notice</h4>
<ul>
<li>{pg.get('notice_days')} days</li>
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
agree = st.checkbox("I agree to rules")

if agree:
    if st.button("Confirm Booking"):
        st.success("Booking Confirmed 🎉")
else:
    st.warning("Accept rules to continue")
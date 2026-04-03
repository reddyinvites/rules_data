import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="PG Rules System", layout="centered")

st.title("🏠 No Hidden Rules (Live Integration)")

# ---------------- GOOGLE AUTH ----------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)

client = gspread.authorize(creds)

# ---------------- YOUR SHEET IDS ----------------
PG_DATA_ID = "1y60dTYBKgkOi7J37jtGK4BkkmUoZF8yD4P5J3xA5q6Q"
PG_RULES_ID = "10y6pbBrz-4lXbes4c4vnvJymlZFIDkZujLn1oMZaCaE"

# ---------------- LOAD PG DATA ----------------
pg_sheet = client.open_by_key(PG_DATA_ID).worksheet("Sheet1")
pg_df = pd.DataFrame(pg_sheet.get_all_records())

# ---------------- LOAD RULES DATA ----------------
rules_sheet = client.open_by_key(PG_RULES_ID).worksheet("rules")
rules_df = pd.DataFrame(rules_sheet.get_all_records())

# ---------------- CLEAN COLUMNS ----------------
pg_df.columns = pg_df.columns.str.strip().str.lower()
rules_df.columns = rules_df.columns.str.strip().str.lower()

# ---------------- IMPORTANT: NORMALIZE NAMES ----------------
pg_df["pg_name"] = pg_df["pg_name"].astype(str).str.strip().str.lower()
rules_df["pg_id"] = rules_df["pg_id"].astype(str).str.strip().str.lower()

# ---------------- PG SELECT ----------------
pg_names = pg_df["pg_name"].dropna().unique().tolist()
selected_pg = st.selectbox("🔍 Select PG", pg_names)

# ---------------- MATCH LOGIC ----------------
selected_pg_clean = selected_pg.strip().lower()

pg_rules = rules_df[rules_df["pg_id"] == selected_pg_clean]

if pg_rules.empty:
    st.error("❌ Rules not found for this PG (Check pg_name vs pg_id match)")
    st.stop()

pg = pg_rules.iloc[0]

# ---------------- UI ----------------
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
    if st.button("✅ Confirm Booking"):
        st.success("🎉 Booking Confirmed!")
else:
    st.warning("⚠️ Accept rules to continue")
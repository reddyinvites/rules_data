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
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

# ---------------- SHEET IDS ----------------
PG_DATA_ID = "1y60dTYBKgkOi7J37jtGK4BkkmUoZF8yD4P5J3xA5q6Q"
PG_RULES_ID = "10y6pbBrz-4lXbes4c4vnvJymlZFIDkZujLn1oMZaCaE"

# ---------------- LOAD DATA ----------------
try:
    pg_sheet = client.open_by_key(PG_DATA_ID).worksheet("Sheet1")
    rules_sheet = client.open_by_key(PG_RULES_ID).worksheet("rules")

    pg_df = pd.DataFrame(pg_sheet.get_all_records())
    rules_df = pd.DataFrame(rules_sheet.get_all_records())

except Exception as e:
    st.error("❌ Google Sheets connection failed. Check permissions.")
    st.stop()

# ---------------- SAFE CLEAN ----------------
pg_df.columns = [str(col).strip().lower() for col in pg_df.columns]
rules_df.columns = [str(col).strip().lower() for col in rules_df.columns]

pg_df = pg_df.fillna("")
rules_df = rules_df.fillna("")

# ---------------- CHECK REQUIRED COLUMN ----------------
if "pg_name" not in pg_df.columns:
    st.error("❌ pg_data Sheet1 must have 'pg_name' column")
    st.stop()

if "pg_id" not in rules_df.columns:
    st.error("❌ pg_rules must have 'pg_id' column")
    st.stop()

# ---------------- NORMALIZE ----------------
pg_df["pg_name"] = pg_df["pg_name"].astype(str).str.strip().str.lower()
rules_df["pg_id"] = rules_df["pg_id"].astype(str).str.strip().str.lower()

# ---------------- SELECT PG ----------------
pg_names = pg_df["pg_name"].dropna().unique().tolist()

if not pg_names:
    st.warning("⚠️ No PG data found")
    st.stop()

selected_pg = st.selectbox("🔍 Select PG", pg_names)

selected_pg_clean = selected_pg.strip().lower()

# ---------------- MATCH RULES ----------------
pg_rules = rules_df[rules_df["pg_id"] == selected_pg_clean]

if pg_rules.empty:
    st.error("❌ Rules not found for this PG (Check pg_name vs pg_id match)")
    st.stop()

pg = pg_rules.iloc[0]

# ---------------- UI ----------------
st.subheader(f"🏠 {selected_pg.title()}")

st.markdown(f"""
<div style="
    background:#FFD84D;
    padding:20px;
    border-radius:12px;
    border:2px solid #0097A7;
">

<h3 style="text-align:center;">RULES & REGULATIONS</h3>

<h4>💰 Money</h4>
<ul>
<li>Rent: ₹{pg.get('rent','N/A')}</li>
<li>Advance: ₹{pg.get('advance','N/A')}</li>
<li>Refund Policy: {pg.get('refund_policy','N/A')}</li>
</ul>

<h4>📅 Notice</h4>
<ul>
<li>{pg.get('notice_days','N/A')} days mandatory</li>
</ul>

<h4>📜 Rules</h4>
<ul>
<li>Guests Allowed: {pg.get('guests_allowed','N/A')}</li>
<li>Cleaning: {pg.get('cleaning','N/A')}</li>
</ul>

<hr>

<h4>🍛 FOOD TIMINGS</h4>
<p>
Breakfast: {pg.get('breakfast_time','N/A')}<br>
Dinner: {pg.get('dinner_time','N/A')}
</p>

</div>
""", unsafe_allow_html=True)

# ---------------- CONFIRM ----------------
st.markdown("### ✅ Confirm Rules")

agree = st.checkbox("I agree to PG rules")

if agree:
    if st.button("✅ Confirm Booking"):
        st.success("🎉 Booking Confirmed!")
else:
    st.warning("⚠️ Please accept rules to continue")
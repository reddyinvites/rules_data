import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="PG Rules Transparency", layout="centered")

# -----------------------
# GOOGLE SHEETS SETUP
# -----------------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)

client = gspread.authorize(creds)

# -----------------------
# SHEET IDS (CHANGE THIS)
# -----------------------
PG_DATA_ID = "YOUR_PG_DATA_SHEET_ID"
PG_RULES_ID = "YOUR_PG_RULES_SHEET_ID"

# -----------------------
# LOAD FUNCTION
# -----------------------
@st.cache_data
def load_sheet(sheet_id, sheet_name):
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# -----------------------
# LOAD DATA
# -----------------------
pg_df = load_sheet(PG_DATA_ID, "Sheet1")
rules_df = load_sheet(PG_RULES_ID, "Sheet1")

# -----------------------
# VALIDATION
# -----------------------
if "pg_id" not in pg_df.columns or "pg_id" not in rules_df.columns:
    st.error("❌ 'pg_id' column missing in sheets")
    st.stop()

# -----------------------
# MERGE DATA
# -----------------------
df = pg_df.merge(rules_df, on="pg_id", how="left")

# -----------------------
# SAFE FUNCTION
# -----------------------
def safe(val):
    if val is None or val == "":
        return "Not mentioned"
    return val

# -----------------------
# TITLE
# -----------------------
st.title("📜 PG Rules Transparency")
st.caption("Hidden rules levu… booking mundhe anni clear ga chupistham ✅")

# -----------------------
# SEARCH (OPTIONAL 🔥)
# -----------------------
search = st.text_input("🔍 Search PG name")

if search:
    df = df[df["pg_name"].str.contains(search, case=False, na=False)]

# -----------------------
# DISPLAY
# -----------------------
for _, row in df.iterrows():

    st.divider()

    # BASIC INFO
    st.subheader(f"🏢 {safe(row.get('pg_name'))}")

    # -----------------------
    # RULES UI 🔥
    # -----------------------
    st.markdown("### 📜 No Hidden Rules")

    # 💰 MONEY
    with st.expander("💰 Money Terms"):
        st.write(f"Rent: ₹{safe(row.get('rent'))}")
        st.write(f"Advance: ₹{safe(row.get('advance'))}")
        st.write(f"Refund: {safe(row.get('refund_policy'))}")

    # 📅 NOTICE
    with st.expander("📅 Notice Period"):
        st.write(f"{safe(row.get('notice_days'))} days mandatory")

    # 🍛 FOOD
    with st.expander("🍛 Food Details"):
        st.write(f"Breakfast: {safe(row.get('breakfast_time'))}")
        st.write(f"Dinner: {safe(row.get('dinner_time'))}")

    # 🚫 RULES
    with st.expander("🚫 PG Rules"):
        st.write(f"Guests Allowed: {safe(row.get('guests_allowed'))}")
        st.write(f"Curfew: {safe(row.get('curfew'))}")
        st.write(f"Cleaning: {safe(row.get('cleaning'))}")

    # -----------------------
    # SMART WARNINGS 🔥
    # -----------------------
    st.markdown("### ⚠️ Important Alerts")

    # Guests
    if str(row.get("guests_allowed")).lower() == "no":
        st.warning("🚫 Guests not allowed")

    # Notice
    try:
        if int(row.get("notice_days", 0)) > 30:
            st.warning("⏳ Long notice period")
    except:
        pass

    # Refund
    if row.get("refund_policy") and "non" in str(row.get("refund_policy")).lower():
        st.error("❗ Partial / Non-refundable")

    # -----------------------
    # STRICTNESS SCORE 🔥
    # -----------------------
    strict_score = 0

    if str(row.get("guests_allowed")).lower() == "no":
        strict_score += 1

    try:
        if int(row.get("notice_days", 0)) > 15:
            strict_score += 1
    except:
        pass

    if row.get("curfew"):
        strict_score += 1

    st.info(f"🔒 PG Strictness Score: {strict_score}/3")

# -----------------------
# EMPTY STATE
# -----------------------
if df.empty:
    st.info("No PGs found")

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="PG Rules", layout="centered")

# -----------------------
# GOOGLE SHEETS SETUP
# -----------------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

# -----------------------
# YOUR SHEET IDS
# -----------------------
PG_DATA_ID = "1y60dTYBKgkOi7J37jtGK4BkkmUoZF8yD4P5J3xA5q6Q"
PG_RULES_ID = "10y6pbBrz-4lXbes4c4vnvJymlZFIDkZujLn1oMZaCaE"

# -----------------------
# SAFE LOAD FUNCTION 🔥
# -----------------------
@st.cache_data
def load_sheet(sheet_id):
    try:
        sh = client.open_by_key(sheet_id)

        try:
            worksheet = sh.worksheet("Sheet1")
        except:
            worksheet = sh.get_worksheet(0)

        data = worksheet.get_all_records()
        return pd.DataFrame(data)

    except Exception as e:
        st.error(f"❌ Sheet Load Error: {e}")
        return pd.DataFrame()

# -----------------------
# LOAD DATA
# -----------------------
pg_df = load_sheet(PG_DATA_ID)
rules_df = load_sheet(PG_RULES_ID)

# -----------------------
# VALIDATION
# -----------------------
if pg_df.empty:
    st.error("❌ PG Data not loaded")
    st.stop()

if rules_df.empty:
    st.error("❌ Rules Data not loaded")
    st.stop()

# Normalize column names (avoid case issues)
pg_df.columns = pg_df.columns.str.strip().str.lower()
rules_df.columns = rules_df.columns.str.strip().str.lower()

# -----------------------
# CHECK pg_id
# -----------------------
if "pg_id" not in pg_df.columns or "pg_id" not in rules_df.columns:
    st.error("❌ 'pg_id' column missing")
    st.write("PG Data Columns:", pg_df.columns)
    st.write("Rules Columns:", rules_df.columns)
    st.stop()

# -----------------------
# MERGE DATA
# -----------------------
df = pd.merge(pg_df, rules_df, on="pg_id", how="left")

# -----------------------
# SAFE FUNCTION
# -----------------------
def safe(x):
    if pd.isna(x) or x == "":
        return "Not mentioned"
    return x

# -----------------------
# UI
# -----------------------
st.title("📜 PG Rules Transparency")
st.caption("Hidden rules levu… booking mundhe anni clear ga chupistham ✅")

# -----------------------
# SEARCH
# -----------------------
search = st.text_input("🔍 Search PG")

if search:
    df = df[df["pg_name"].astype(str).str.contains(search, case=False, na=False)]

# -----------------------
# DISPLAY
# -----------------------
for _, row in df.iterrows():

    st.divider()
    st.subheader(f"🏢 {safe(row.get('pg_name'))}")

    st.markdown("### 📜 No Hidden Rules")

    # 💰 MONEY
    with st.expander("💰 Money"):
        st.write("Rent:", safe(row.get("rent")))
        st.write("Advance:", safe(row.get("advance")))
        st.write("Refund:", safe(row.get("refund_policy")))

    # 📅 NOTICE
    with st.expander("📅 Notice"):
        st.write("Notice Days:", safe(row.get("notice_days")))

    # 🍛 FOOD
    with st.expander("🍛 Food"):
        st.write("Breakfast:", safe(row.get("breakfast_time")))
        st.write("Dinner:", safe(row.get("dinner_time")))

    # 🚫 RULES
    with st.expander("🚫 Rules"):
        st.write("Guests:", safe(row.get("guests_allowed")))
        st.write("Curfew:", safe(row.get("curfew")))
        st.write("Cleaning:", safe(row.get("cleaning")))

    # -----------------------
    # ALERTS
    # -----------------------
    st.markdown("### ⚠️ Alerts")

    if str(row.get("guests_allowed")).lower() == "no":
        st.warning("🚫 Guests not allowed")

    try:
        if int(row.get("notice_days", 0)) > 30:
            st.warning("⏳ Long notice period")
    except:
        pass

    if row.get("refund_policy") and "non" in str(row.get("refund_policy")).lower():
        st.error("❗ Non-refundable / partial refund")

    # -----------------------
    # STRICTNESS SCORE
    # -----------------------
    score = 0

    if str(row.get("guests_allowed")).lower() == "no":
        score += 1

    try:
        if int(row.get("notice_days", 0)) > 15:
            score += 1
    except:
        pass

    if row.get("curfew"):
        score += 1

    st.info(f"🔒 Strictness Score: {score}/3")

# -----------------------
# EMPTY STATE
# -----------------------
if df.empty:
    st.info("No PGs found")
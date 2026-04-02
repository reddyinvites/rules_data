import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="PG Rules", layout="centered")

# -----------------------
# GOOGLE SETUP
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
# SHEET IDS
# -----------------------
PG_DATA_ID = "1y60dTYBKgkOi7J37jtGK4BkkmUoZF8yD4P5J3xA5q6Q"
PG_RULES_ID = "10y6pbBrz-4lXbes4c4vnvJymlZFIDkZujLn1oMZaCaE"

# -----------------------
# LOAD FUNCTION (STRONG 🔥)
# -----------------------
def load_sheet(sheet_id, name):
    try:
        sh = client.open_by_key(sheet_id)

        # try all worksheets one by one
        for ws in sh.worksheets():
            data = ws.get_all_records()
            if len(data) > 0:
                st.success(f"✅ Loaded {name} from sheet: {ws.title}")
                return pd.DataFrame(data)

        st.warning(f"⚠️ {name} sheet is empty")
        return pd.DataFrame()

    except Exception as e:
        st.error(f"❌ Error loading {name}: {e}")
        return pd.DataFrame()

# -----------------------
# LOAD DATA
# -----------------------
pg_df = load_sheet(PG_DATA_ID, "PG Data")
rules_df = load_sheet(PG_RULES_ID, "Rules Data")

# -----------------------
# DEBUG SHOW 🔥
# -----------------------
st.write("PG Data Rows:", len(pg_df))
st.write("Rules Data Rows:", len(rules_df))

# -----------------------
# STOP IF EMPTY
# -----------------------
if pg_df.empty:
    st.error("❌ PG Data not loaded")
    st.stop()

if rules_df.empty:
    st.error("❌ Rules Data not loaded")
    st.stop()

# -----------------------
# CLEAN COLUMNS
# -----------------------
pg_df.columns = pg_df.columns.str.strip().str.lower()
rules_df.columns = rules_df.columns.str.strip().str.lower()

# -----------------------
# CHECK pg_id
# -----------------------
if "pg_id" not in pg_df.columns or "pg_id" not in rules_df.columns:
    st.error("❌ pg_id missing")
    st.write("PG columns:", pg_df.columns)
    st.write("Rules columns:", rules_df.columns)
    st.stop()

# -----------------------
# MERGE
# -----------------------
df = pd.merge(pg_df, rules_df, on="pg_id", how="left")

# -----------------------
# SAFE
# -----------------------
def safe(x):
    if pd.isna(x) or x == "":
        return "Not mentioned"
    return x

# -----------------------
# UI
# -----------------------
st.title("📜 PG Rules Transparency")

for _, row in df.iterrows():
    st.divider()
    st.subheader(safe(row.get("pg_name")))

    with st.expander("💰 Money"):
        st.write("Rent:", safe(row.get("rent")))
        st.write("Advance:", safe(row.get("advance")))
        st.write("Refund:", safe(row.get("refund_policy")))

    with st.expander("📅 Notice"):
        st.write("Days:", safe(row.get("notice_days")))

    with st.expander("🍛 Food"):
        st.write("Breakfast:", safe(row.get("breakfast_time")))
        st.write("Dinner:", safe(row.get("dinner_time")))

    with st.expander("🚫 Rules"):
        st.write("Guests:", safe(row.get("guests_allowed")))
        st.write("Curfew:", safe(row.get("curfew")))
        st.write("Cleaning:", safe(row.get("cleaning")))
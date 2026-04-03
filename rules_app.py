import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Dynamic PG Rules", layout="centered")

st.title("🏠 No Hidden Rules (Live Data)")

# -------------------------
# GOOGLE SHEETS CONNECTION
# -------------------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)

client = gspread.authorize(creds)

# 👉 YOUR SHEET ID
SHEET_ID = "1y60dTYBKgkOiXXXXXXXXXXXX"  # replace with your real ID

sheet = client.open_by_key(SHEET_ID).worksheet("Sheet1")

data = sheet.get_all_records()
df = pd.DataFrame(data)

# -------------------------
# PG SELECT
# -------------------------
pg_names = df["pg_name"].unique().tolist()

selected_pg = st.selectbox("🔍 Select PG", pg_names)

pg_data = df[df["pg_name"] == selected_pg].iloc[0]

# -------------------------
# RULES UI
# -------------------------
def show_pg_rules(pg):

    st.subheader(f"🏠 {pg['pg_name']}")

    st.markdown(f"""
    <div style="
        background-color:#FFD84D;
        padding:20px;
        border-radius:12px;
        border:3px solid #0097A7;
        font-family:Arial;
    ">

    <h3 style="text-align:center;">RULES & REGULATIONS</h3>

    <h4>💰 Money</h4>
    <ul>
    <li>Rent: <b>₹{pg['rent']}</b></li>
    <li>Advance: <b>₹{pg['advance']}</b></li>
    <li>Refund: <b>₹{pg['refund']}</b></li>
    </ul>

    <h4>📅 Notice</h4>
    <ul>
    <li>{pg['notice_days']} days mandatory</li>
    </ul>

    <h4>📜 Rules</h4>
    <ol>
    <li>Rent before 5th</li>
    <li>Guests: ₹{pg['guest_charge']}/day</li>
    <li>Curfew: {pg['curfew']}</li>
    <li>No smoking/alcohol</li>
    <li>Damage charges apply</li>
    </ol>

    <hr>

    <h4>🍛 FOOD TIMINGS</h4>
    <p>
    Breakfast: <b>{pg['breakfast']}</b><br>
    Lunch: <b>{pg['lunch']}</b><br>
    Dinner: <b>{pg['dinner']}</b>
    </p>

    </div>
    """, unsafe_allow_html=True)


# -------------------------
# AGREEMENT
# -------------------------
def rules_agreement():
    st.markdown("### ✅ Confirm Rules")

    agree = st.checkbox("I agree to PG rules")

    if agree:
        if st.button("✅ Confirm Booking"):
            st.success("🎉 Booking Confirmed!")
    else:
        st.warning("⚠️ Accept rules to continue")


# -------------------------
# DISPLAY
# -------------------------
show_pg_rules(pg_data)
rules_agreement()
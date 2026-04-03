import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="PG Rules Live", layout="centered")

st.title("🏠 No Hidden Rules (Live Data)")

# -------------------------
# GOOGLE SHEETS CONNECTION
# -------------------------
try:
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)

    # ✅ YOUR REAL SHEET ID
    SHEET_ID = "1y60dTYBKgkOi7J37jtGK4BkkmUoZF8yD4P5J3xA5q6Q"

    spreadsheet = client.open_by_key(SHEET_ID)
    worksheet = spreadsheet.worksheet("Sheet1")

    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

except Exception as e:
    st.error("❌ Google Sheet connect avvaledu. Check permissions.")
    st.stop()

# -------------------------
# CHECK DATA
# -------------------------
if df.empty:
    st.warning("⚠️ Sheet lo data ledu")
    st.stop()

# -------------------------
# PG SELECT
# -------------------------
pg_names = df["pg_name"].dropna().unique().tolist()

selected_pg = st.selectbox("🔍 Select PG", pg_names)

pg = df[df["pg_name"] == selected_pg].iloc[0]

# -------------------------
# RULES UI
# -------------------------
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
st.markdown("### ✅ Confirm Rules")

agree = st.checkbox("I agree to PG rules")

if agree:
    if st.button("✅ Confirm Booking"):
        st.success("🎉 Booking Confirmed!")
else:
    st.warning("⚠️ Accept rules to continue")
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="PG Rules System", layout="centered")
st.title("🏠 PG Rules System")

# ---------------- ROLE ----------------
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

# ---------------- CACHE LOAD ----------------
@st.cache_data(ttl=300)
def load_sheet(sheet_id, sheet_name):
    try:
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        if df.empty:
            return pd.DataFrame()

        df.columns = [str(c).strip().lower() for c in df.columns]
        df = df.fillna("")
        return df

    except Exception as e:
        st.error(f"❌ Error loading '{sheet_name}' → {e}")
        return pd.DataFrame()

# ---------------- LOAD PG DATA ----------------
pg_df = load_sheet(PG_DATA_ID, "Sheet1")

if pg_df.empty:
    st.warning("⚠️ PG data not found")
    st.stop()

pg_df["pg_name"] = pg_df["pg_name"].str.strip().str.lower()
pg_names = pg_df["pg_name"].unique().tolist()

# =========================
# 👤 USER SECTION (PREMIUM UI)
# =========================
if role == "User":

    selected_pg = st.selectbox("🔍 Select PG", pg_names)

    rules_df = load_sheet(RULES_ID, "rules")

    if rules_df.empty:
        st.warning("⚠️ No rules available")
        st.stop()

    rules_df["pg_name"] = rules_df["pg_name"].str.strip().str.lower()
    pg_rules = rules_df[rules_df["pg_name"] == selected_pg]

    if pg_rules.empty:
        st.warning("⚠️ No rules found")
        st.stop()

    pg = pg_rules.iloc[-1]

    st.subheader(f"🏠 {selected_pg.title()}")

    # -------- STYLE --------
    st.markdown("""
    <style>
    .card {
        background: white;
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 15px;
    }
    .title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .highlight {
        font-size: 22px;
        font-weight: bold;
        color: #2E86C1;
    }
    </style>
    """, unsafe_allow_html=True)

    # -------- CARDS --------
    st.markdown(f"""
    <div class="card">
        <div class="title">💰 Pricing</div>
        <div class="highlight">₹{pg.get('rent')}</div>
        <p>Advance: ₹{pg.get('advance')}</p>
        <p>Refund: {pg.get('refund_policy')}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
        <div class="title">📅 Notice</div>
        <p>{pg.get('notice_days')} days</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
        <div class="title">📜 Basic Rules</div>
        <p>Guests: {pg.get('guests_allowed')}</p>
        <p>Cleaning: {pg.get('cleaning')}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
        <div class="title">🔒 Advanced</div>
        <p>Curfew: {pg.get('curfew')}</p>
        <p>Smoking: {pg.get('smoking')}</p>
        <p>Alcohol: {pg.get('alcohol')}</p>
        <p>Late Entry: {pg.get('late_entry')}</p>
        <p>Visitors: {pg.get('visitors_time')}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
        <div class="title">🏠 Facilities</div>
        <p>WiFi: {pg.get('wifi')}</p>
        <p>Laundry: {pg.get('laundry')}</p>
        <p>Parking: {pg.get('parking')}</p>
        <p>Power: {pg.get('power_backup')}</p>
        <p>Room: {pg.get('room_type')}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
        <div class="title">🍛 Food</div>
        <p>Breakfast: {pg.get('breakfast_time')}</p>
        <p>Dinner: {pg.get('dinner_time')}</p>
    </div>
    """, unsafe_allow_html=True)

    st.caption(f"🕒 Last Updated: {pg.get('timestamp','N/A')}")

    agree = st.checkbox("I agree to rules")

    if agree:
        st.success("✅ Ready to book")
    else:
        st.warning("⚠️ Accept rules")

# =========================
# 🛠 ADMIN SECTION
# =========================
if role == "Admin":

    st.subheader("🛠 Manage PG Rules")

    rules_sheet = client.open_by_key(RULES_ID).worksheet("rules")
    rules_df = load_sheet(RULES_ID, "rules")

    if not rules_df.empty:
        rules_df["pg_name"] = rules_df["pg_name"].str.strip().str.lower()

    pg_name = st.selectbox("Select PG", pg_names)
    pg_rows = rules_df[rules_df["pg_name"] == pg_name] if not rules_df.empty else pd.DataFrame()

    if not pg_rows.empty:
        latest = pg_rows.iloc[-1]
        st.info(f"🕒 Last Updated: {latest.get('timestamp','N/A')}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✏️ Edit"):
                st.session_state["edit_mode"] = True
                st.session_state["edit_data"] = latest.to_dict()

        with col2:
            if st.button("🗑 Delete"):

                all_data = rules_sheet.get_all_values()
                header = all_data[0]

                new_data = [header] + [
                    row for row in all_data[1:]
                    if row[0].strip().lower() != pg_name
                ]

                rules_sheet.clear()
                rules_sheet.update("A1", new_data)
                st.cache_data.clear()
                st.success("Deleted")
                st.rerun()

    if "edit_mode" not in st.session_state:
        st.session_state["edit_mode"] = False

    pg = st.session_state.get("edit_data", {}) if st.session_state["edit_mode"] else {}

    rent = st.number_input("Rent", 0, value=int(pg.get("rent", 0)))
    advance = st.number_input("Advance", 0, value=int(pg.get("advance", 0)))
    refund_policy = st.text_input("Refund", pg.get("refund_policy", ""))
    notice_days = st.number_input("Notice", 0, value=int(pg.get("notice_days", 0)))

    guests_allowed = st.selectbox("Guests", ["Yes","No"], index=0 if pg.get("guests_allowed","Yes")=="Yes" else 1)
    cleaning = st.selectbox("Cleaning", ["Daily","Weekly","Monthly"],
                           index=["Daily","Weekly","Monthly"].index(pg.get("cleaning","Daily"))
                           if pg.get("cleaning","Daily") in ["Daily","Weekly","Monthly"] else 0)

    curfew = st.text_input("Curfew", pg.get("curfew",""))
    smoking = st.selectbox("Smoking", ["No","Yes"], index=1 if pg.get("smoking")=="Yes" else 0)
    alcohol = st.selectbox("Alcohol", ["No","Yes"], index=1 if pg.get("alcohol")=="Yes" else 0)
    late_entry = st.selectbox("Late Entry", ["No","Yes"], index=1 if pg.get("late_entry")=="Yes" else 0)
    visitors_time = st.text_input("Visitors", pg.get("visitors_time",""))

    wifi = st.selectbox("WiFi", ["Yes","No"], index=0 if pg.get("wifi")=="Yes" else 1)
    laundry = st.selectbox("Laundry", ["Yes","No"], index=0 if pg.get("laundry")=="Yes" else 1)
    parking = st.selectbox("Parking", ["Yes","No"], index=0 if pg.get("parking")=="Yes" else 1)
    power_backup = st.selectbox("Power", ["Yes","No"], index=0 if pg.get("power_backup")=="Yes" else 1)
    room_type = st.selectbox("Room", ["AC","Non-AC","Both"],
                            index=["AC","Non-AC","Both"].index(pg.get("room_type","AC"))
                            if pg.get("room_type","AC") in ["AC","Non-AC","Both"] else 0)

    breakfast_time = st.text_input("Breakfast", pg.get("breakfast_time",""))
    dinner_time = st.text_input("Dinner", pg.get("dinner_time",""))

    if st.button("💾 Save / Update"):

        all_data = rules_sheet.get_all_values()
        header = all_data[0]

        new_data = [header] + [
            row for row in all_data[1:]
            if row[0].strip().lower() != pg_name
        ]

        new_data.append([
            pg_name.strip().lower(),
            rent, advance, refund_policy, notice_days,
            breakfast_time, dinner_time,
            guests_allowed, cleaning, curfew,
            smoking, alcohol, late_entry, visitors_time,
            wifi, laundry, parking, power_backup, room_type,
            str(datetime.now())
        ])

        rules_sheet.clear()
        rules_sheet.update("A1", new_data)

        st.cache_data.clear()
        st.session_state["edit_mode"] = False
        st.success("✅ Updated")
        st.rerun()
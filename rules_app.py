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

# ---------------- CACHE SHEET LOAD ----------------
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
# 👤 USER SECTION
# =========================
if role == "User":

    st.subheader("🔍 Select PG")
    selected_pg = st.selectbox("Choose PG", pg_names)

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
    st.info(f"🕒 Last Updated: {pg.get('timestamp','N/A')}")

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
    <li>{pg.get('notice_days')} days</li>
    </ul>

    <h4>📜 Basic Rules</h4>
    <ul>
    <li>Guests: {pg.get('guests_allowed')}</li>
    <li>Cleaning: {pg.get('cleaning')}</li>
    </ul>

    <h4>🔒 Advanced Rules</h4>
    <ul>
    <li>Curfew: {pg.get('curfew')}</li>
    <li>Smoking: {pg.get('smoking')}</li>
    <li>Alcohol: {pg.get('alcohol')}</li>
    <li>Late Entry: {pg.get('late_entry')}</li>
    <li>Visitors: {pg.get('visitors_time')}</li>
    </ul>

    <h4>🏠 Facilities</h4>
    <ul>
    <li>WiFi: {pg.get('wifi')}</li>
    <li>Laundry: {pg.get('laundry')}</li>
    <li>Parking: {pg.get('parking')}</li>
    <li>Power Backup: {pg.get('power_backup')}</li>
    <li>Room Type: {pg.get('room_type')}</li>
    </ul>

    <hr>

    <h4>🍛 FOOD TIMINGS</h4>
    <p>
    Breakfast: {pg.get('breakfast_time')}<br>
    Dinner: {pg.get('dinner_time')}
    </p>
    </div>
    """, unsafe_allow_html=True)

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

    # -------- EXISTING --------
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
                st.success("🗑 Deleted successfully")
                st.rerun()

    else:
        st.warning("No rules found. Add new.")

    # -------- SESSION --------
    if "edit_mode" not in st.session_state:
        st.session_state["edit_mode"] = False

    pg = st.session_state.get("edit_data", {}) if st.session_state["edit_mode"] else {}

    # -------- FORM --------
    st.markdown("### 💰 Money")
    rent = st.number_input("Rent", 0, value=int(pg.get("rent", 0)))
    advance = st.number_input("Advance", 0, value=int(pg.get("advance", 0)))
    refund_policy = st.text_input("Refund Policy", pg.get("refund_policy", ""))

    st.markdown("### 📅 Notice")
    notice_days = st.number_input("Notice Days", 0, value=int(pg.get("notice_days", 0)))

    st.markdown("### 📜 Basic Rules")
    guests_allowed = st.selectbox("Guests Allowed", ["Yes", "No"],
                                 index=0 if pg.get("guests_allowed","Yes")=="Yes" else 1)

    cleaning = st.selectbox("Cleaning", ["Daily","Weekly","Monthly"],
                           index=["Daily","Weekly","Monthly"].index(pg.get("cleaning","Daily"))
                           if pg.get("cleaning","Daily") in ["Daily","Weekly","Monthly"] else 0)

    st.markdown("### 🔒 Advanced Rules")
    curfew = st.text_input("Curfew Time", pg.get("curfew",""))
    smoking = st.selectbox("Smoking", ["No","Yes"], index=1 if pg.get("smoking")=="Yes" else 0)
    alcohol = st.selectbox("Alcohol", ["No","Yes"], index=1 if pg.get("alcohol")=="Yes" else 0)
    late_entry = st.selectbox("Late Entry", ["No","Yes"], index=1 if pg.get("late_entry")=="Yes" else 0)
    visitors_time = st.text_input("Visitors Time", pg.get("visitors_time",""))

    st.markdown("### 🏠 Facilities")
    wifi = st.selectbox("WiFi", ["Yes","No"], index=0 if pg.get("wifi")=="Yes" else 1)
    laundry = st.selectbox("Laundry", ["Yes","No"], index=0 if pg.get("laundry")=="Yes" else 1)
    parking = st.selectbox("Parking", ["Yes","No"], index=0 if pg.get("parking")=="Yes" else 1)
    power_backup = st.selectbox("Power Backup", ["Yes","No"], index=0 if pg.get("power_backup")=="Yes" else 1)

    room_type = st.selectbox("Room Type", ["AC","Non-AC","Both"],
                            index=["AC","Non-AC","Both"].index(pg.get("room_type","AC"))
                            if pg.get("room_type","AC") in ["AC","Non-AC","Both"] else 0)

    st.markdown("### 🍛 Food")
    breakfast_time = st.text_input("Breakfast Time", pg.get("breakfast_time",""))
    dinner_time = st.text_input("Dinner Time", pg.get("dinner_time",""))

    # -------- SAVE --------
    if st.button("💾 Save / Update"):

        all_data = rules_sheet.get_all_values()
        header = all_data[0] if all_data else [
            "pg_name","rent","advance","refund_policy","notice_days",
            "breakfast_time","dinner_time","guests_allowed","cleaning",
            "curfew","smoking","alcohol","late_entry","visitors_time",
            "wifi","laundry","parking","power_backup","room_type","timestamp"
        ]

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

        st.success("✅ Rules updated successfully")
        st.rerun()
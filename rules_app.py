import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="PG Rules System", layout="centered")
st.title("🏠 PG Rules System")

role = st.radio("Login as:", ["User", "Admin"])

# ---------------- AUTH ----------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(creds)

PG_DATA_ID = "YOUR_PG_ID"
RULES_ID = "YOUR_RULES_ID"

# ---------------- CACHE ----------------
@st.cache_data(ttl=300)
def load_sheet(sheet_id, sheet_name):
    try:
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
        df = pd.DataFrame(sheet.get_all_records())
        if df.empty:
            return pd.DataFrame()
        df.columns = [c.strip().lower() for c in df.columns]
        return df.fillna("")
    except:
        return pd.DataFrame()

pg_df = load_sheet(PG_DATA_ID, "Sheet1")
pg_df["pg_name"] = pg_df["pg_name"].str.lower()
pg_names = pg_df["pg_name"].unique().tolist()

# ================= USER =================
if role == "User":

    selected_pg = st.selectbox("Select PG", pg_names)

    rules_df = load_sheet(RULES_ID, "rules")
    rules_df["pg_name"] = rules_df["pg_name"].str.lower()

    pg = rules_df[rules_df["pg_name"] == selected_pg].iloc[-1]

    def card(title, content):
        st.markdown(f"""
        <div style="background:white;padding:12px;border-radius:10px;margin-bottom:10px">
        <b>{title}</b><br>{content}
        </div>
        """, unsafe_allow_html=True)

    card("⏰ Freedom",
         f"Curfew: {pg['curfew']}<br>Late Entry: {pg['late_entry']}<br>Visitors: {pg['visitors_time']}")

    card("🚭 Lifestyle",
         f"Smoking: {pg['smoking']}<br>Alcohol: {pg['alcohol']}")

    card("🍛 Food",
         f"{pg['breakfast_time']} / {pg['lunch_time']} / {pg['dinner_time']}")

    card("📅 Notice",
         f"{pg['notice_days']} days<br>{pg['notice_policy']}")

    card("🔐 Security",
         f"ID: {pg['id_required']}<br>Gate Strict: {pg['gate_strict']}")

    card("⚡ Utilities",
         f"Power: {pg['power_included']}<br>Maintenance: {pg['maintenance_charge']}")

    card("🚫 Restrictions",
         f"Cooking: {pg['cooking_allowed']}<br>Music: {pg['music_allowed']}")

    card("🔑 Penalties",
         f"Key Loss: {pg['key_loss_charge']}<br>Damage: {pg['damage_policy']}")

# ================= ADMIN =================
if role == "Admin":

    rules_sheet = client.open_by_key(RULES_ID).worksheet("rules")

    pg_name = st.selectbox("Select PG", pg_names)

    guests_allowed = st.selectbox("Guests Allowed", ["Yes","No"])
    cleaning = st.selectbox("Cleaning", ["Daily","Weekly","Twice Weekly","Thrice Weekly"])

    curfew = st.text_input("Curfew Time")
    late_entry = st.selectbox("Late Entry", ["No","Yes"])

    if guests_allowed == "Yes":
        visitors_time = st.text_input("Visitors Timing")
    else:
        visitors_time = "Not Allowed"

    smoking = st.selectbox("Smoking", ["No","Yes"])
    alcohol = st.selectbox("Alcohol", ["No","Yes"])

    notice_days = st.number_input("Notice Days", 0)
    notice_policy = st.text_area("Notice Policy")

    col1,col2,col3 = st.columns(3)
    breakfast_time = col1.text_input("Breakfast")
    lunch_time = col2.text_input("Lunch")
    dinner_time = col3.text_input("Dinner")

    # NEW RULES
    id_required = st.selectbox("ID Required", ["Yes","No"])
    gate_strict = st.selectbox("Gate Strict", ["Yes","No"])
    power_included = st.selectbox("Power Included", ["Yes","No"])
    maintenance_charge = st.text_input("Maintenance")

    cooking_allowed = st.selectbox("Cooking Allowed", ["Yes","No"])
    music_allowed = st.selectbox("Music Allowed", ["Yes","No"])

    key_loss_charge = st.text_input("Key Loss Charge")
    damage_policy = st.text_input("Damage Policy")

    if st.button("Save"):

        all_data = rules_sheet.get_all_values()
        header = all_data[0]

        new_data = [header] + [
            row for row in all_data[1:]
            if row[0].lower() != pg_name
        ]

        new_data.append([
            pg_name,
            notice_days,
            notice_policy,
            breakfast_time,
            lunch_time,
            dinner_time,
            guests_allowed,
            cleaning,
            curfew,
            smoking,
            alcohol,
            late_entry,
            visitors_time,
            id_required,
            gate_strict,
            power_included,
            maintenance_charge,
            cooking_allowed,
            music_allowed,
            key_loss_charge,
            damage_policy,
            str(datetime.now())
        ])

        rules_sheet.clear()
        rules_sheet.update("A1", new_data)

        st.cache_data.clear()
        st.success("Saved")
        st.rerun()
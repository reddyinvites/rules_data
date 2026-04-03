import streamlit as st

st.set_page_config(page_title="Dynamic PG Rules", layout="centered")

st.title("🏠 No Hidden Rules (Dynamic PG)")

# -------------------------
# MULTIPLE PG DATA
# -------------------------
pg_list = {
    "Sri Manjunatha PG": {
        "rent": 6000,
        "advance": 2000,
        "refund": 1000,
        "notice_days": 30,
        "guest_charge": 350,
        "curfew": "10 PM",
        "breakfast": "7:30 – 10:00 AM",
        "lunch": "12:30 – 2:30 PM",
        "dinner": "7:30 – 10:00 PM"
    },
    "Venkateshwara PG": {
        "rent": 7500,
        "advance": 3000,
        "refund": 1500,
        "notice_days": 15,
        "guest_charge": 500,
        "curfew": "9 PM",
        "breakfast": "8:00 – 10:30 AM",
        "lunch": "1:00 – 3:00 PM",
        "dinner": "8:00 – 10:30 PM"
    },
    "Sai Residency PG": {
        "rent": 5000,
        "advance": 1500,
        "refund": 500,
        "notice_days": 20,
        "guest_charge": 200,
        "curfew": "No Curfew",
        "breakfast": "7:00 – 9:30 AM",
        "lunch": "12:00 – 2:00 PM",
        "dinner": "7:00 – 9:00 PM"
    }
}

# -------------------------
# PG SELECTION
# -------------------------
selected_pg = st.selectbox("🔍 Select PG", list(pg_list.keys()))

pg_data = pg_list[selected_pg]

# -------------------------
# RULES UI FUNCTION
# -------------------------
def show_pg_rules(pg_name, pg_data):

    st.subheader(f"🏠 {pg_name}")

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
    <li>Rent: <b>₹{pg_data['rent']}</b></li>
    <li>Advance: <b>₹{pg_data['advance']}</b></li>
    <li>Refund: <b>₹{pg_data['refund']}</b></li>
    </ul>

    <h4>📅 Notice</h4>
    <ul>
    <li>{pg_data['notice_days']} days mandatory</li>
    </ul>

    <h4>📜 Rules</h4>
    <ol>
    <li>Rent before 5th</li>
    <li>Guests: ₹{pg_data['guest_charge']}/day</li>
    <li>Curfew: {pg_data['curfew']}</li>
    <li>No smoking/alcohol</li>
    <li>Damage charges apply</li>
    </ol>

    <hr>

    <h4>🍛 FOOD TIMINGS</h4>
    <p>
    Breakfast: <b>{pg_data['breakfast']}</b><br>
    Lunch: <b>{pg_data['lunch']}</b><br>
    Dinner: <b>{pg_data['dinner']}</b>
    </p>

    </div>
    """, unsafe_allow_html=True)


# -------------------------
# AGREEMENT FUNCTION
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
show_pg_rules(selected_pg, pg_data)
rules_agreement()
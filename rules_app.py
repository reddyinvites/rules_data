import streamlit as st

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="PG Rules", layout="centered")

st.title("🏠 No Hidden Rules")

# -------------------------
# FUNCTION: RULES UI
# -------------------------
def show_pg_rules(pg_data):

    st.markdown(f"""
    <div style="
        background-color:#FFD84D;
        padding:20px;
        border-radius:12px;
        border:3px solid #0097A7;
        font-family:Arial;
    ">

    <h2 style="color:#006064; text-align:center;">
    RULES & REGULATIONS
    </h2>

    <h4>💰 Money</h4>
    <ul>
    <li>Rent: <b>₹{pg_data['rent']}</b></li>
    <li>Advance: <b>₹{pg_data['advance']}</b></li>
    <li>Refund: <b>₹{pg_data['refund']}</b> (remaining non-refundable)</li>
    </ul>

    <h4>📅 Notice</h4>
    <ul>
    <li>{pg_data['notice_days']} days mandatory before vacating</li>
    </ul>

    <h4>📜 Rules</h4>
    <ol>
    <li>Rent should be paid before 5th of every month</li>
    <li>Guests allowed with ₹{pg_data['guest_charge']}/day</li>
    <li>Curfew time: {pg_data['curfew']}</li>
    <li>Smoking & alcohol not allowed</li>
    <li>Damage charges applicable</li>
    <li>Lost key fine: ₹300</li>
    </ol>

    <hr>

    <h4 style="color:#BF360C;">🍛 FOOD TIMINGS</h4>
    <p>
    Breakfast: <b>{pg_data['breakfast']}</b><br>
    Lunch: <b>{pg_data['lunch']}</b><br>
    Dinner: <b>{pg_data['dinner']}</b>
    </p>

    <p style="color:red; font-weight:bold;">
    Note: Rules follow cheyakapothe immediate vacate cheyyali.
    </p>

    </div>
    """, unsafe_allow_html=True)


# -------------------------
# FUNCTION: AGREEMENT
# -------------------------
def rules_agreement():

    st.markdown("### ✅ Confirmation")

    agree = st.checkbox("I have read and agree to all PG rules")

    if agree:
        if st.button("✅ Confirm & Book"):
            st.success("🎉 Booking Confirmed! No Hidden Rules 👍")
    else:
        st.warning("⚠️ Please accept rules to continue")


# -------------------------
# MAIN EXECUTION (IMPORTANT)
# -------------------------
if __name__ == "__main__":

    # SAMPLE DATA (you can change later)
    pg_data = {
        "rent": 6000,
        "advance": 2000,
        "refund": 1000,
        "notice_days": 30,
        "guest_charge": 350,
        "curfew": "10:00 PM",
        "breakfast": "7:30 – 10:00 AM",
        "lunch": "12:30 – 2:30 PM",
        "dinner": "7:30 – 10:00 PM"
    }

    # SHOW UI
    show_pg_rules(pg_data)
    rules_agreement()
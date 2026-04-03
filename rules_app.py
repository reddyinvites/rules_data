import streamlit as st

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
    <li>Lost key: ₹300</li>
    </ol>

    <hr>

    <h4>🍛 FOOD TIMINGS</h4>
    <p>
    Breakfast: <b>{pg_data['breakfast']}</b><br>
    Lunch: <b>{pg_data['lunch']}</b><br>
    Dinner: <b>{pg_data['dinner']}</b>
    </p>

    <p style="color:red; font-weight:bold;">
    Note: Follow rules strictly
    </p>

    </div>
    """, unsafe_allow_html=True)


def rules_agreement():

    st.markdown("### ✅ Confirm Rules")

    agree = st.checkbox("I agree to PG rules")

    if agree:
        if st.button("✅ Confirm Booking"):
            st.success("🎉 Booking Confirmed!")
    else:
        st.warning("⚠️ Accept rules to continue")
# services/donation.py
import streamlit as st

def display_donation_support():
    """Show donation options for user support."""
    st.markdown("### ☕ Support the Project")
    st.markdown("If you find this guide helpful, consider supporting us")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🥤 Buy Me a Coffee")
        st.markdown("$5 - Keep us caffeinated")
        if st.button("Support $5"):
            st.info("🔗 Redirect to payment page (Stripe/PayPal integration needed)")
    
    with col2:
        st.markdown("#### 🍕 Pizza Fund")
        st.markdown("$15 - Fuel our development")
        if st.button("Support $15"):
            st.info("🔗 Redirect to payment page")
    
    with col3:
        st.markdown("#### 🌟 Become a Patron")
        st.markdown("Monthly support")
        if st.button("Monthly Support"):
            st.info("🔗 Redirect to Patreon")
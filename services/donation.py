# services/donation.py
import streamlit as st
from services.paypal_service import display_donation_buttons, handle_paypal_callback
from services.i18n import t

def display_donation_support():
    """Show donation options with PayPal integration."""
    # Handle incoming PayPal callbacks
    handle_paypal_callback()
    
    st.markdown(f"### ☕ {t('support_us')}")
    st.markdown(t('donation_desc', 'Your support helps us create better travel guides and keep the site free for everyone!'))
    
    # PayPal donation buttons
    display_donation_buttons()
    
    st.markdown(f"""
    <div style="
        border:1px solid #e2e8f0;
        border-radius:1rem;
        padding:1rem;
        margin-top:1rem;
        text-align:center;
        background:#f8fafc;
    ">
        <p style="color:#64748b;font-size:0.85rem;margin:0;">
            &#128274; {t('paypal_secured', 'Secured by PayPal')} &bull; 
            {t('donation_privacy', 'Your information is safe and never stored on our servers')}
        </p>
    </div>
    """, unsafe_allow_html=True)
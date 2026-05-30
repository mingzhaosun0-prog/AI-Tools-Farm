# services/api_service.py
import streamlit as st
import json
import os
import hashlib
from datetime import datetime, timedelta

API_KEYS_PATH = "data/api_keys.json"

def generate_api_key(business_name, email):
    """Generate API key for business partners."""
    timestamp = datetime.now().isoformat()
    raw_key = f"{business_name}{email}{timestamp}"
    api_key = hashlib.sha256(raw_key.encode()).hexdigest()[:32]
    
    key_data = {
        "api_key": api_key,
        "business_name": business_name,
        "email": email,
        "created": timestamp,
        "calls_limit": 10000,
        "calls_used": 0,
        "tier": "business",
        "price_monthly": 99
    }
    
    if not os.path.exists(API_KEYS_PATH):
        os.makedirs(os.path.dirname(API_KEYS_PATH), exist_ok=True)
        with open(API_KEYS_PATH, 'w') as f:
            json.dump([], f)
    
    with open(API_KEYS_PATH, 'r') as f:
        keys = json.load(f)
    
    keys.append(key_data)
    
    with open(API_KEYS_PATH, 'w') as f:
        json.dump(keys, f, indent=2)
    
    return api_key

def display_api_offering():
    """Show API access options for businesses."""
    st.markdown("### 🔌 API Access for Travel Businesses")
    st.markdown("Integrate our travel data into your platform")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🆓 Free Tier")
        st.markdown("- 100 calls/day")
        st.markdown("- Basic attraction data")
        st.markdown("- 7-day history")
        st.markdown("**$0/month**")
    
    with col2:
        st.markdown("#### 💼 Business Tier")
        st.markdown("- 10,000 calls/month")
        st.markdown("- Full travel data")
        st.markdown("- 1-year history")
        st.markdown("- Email support")
        st.markdown("**$99/month**")
    
    with col3:
        st.markdown("#### 🏢 Enterprise Tier")
        st.markdown("- Unlimited calls")
        st.markdown("- Custom data integration")
        st.markdown("- SLA guarantee")
        st.markdown("- Dedicated support")
        st.markdown("**Custom pricing**")
    
    with st.form("api_request"):
        business_name = st.text_input("Business name")
        email = st.text_input("Contact email")
        
        if st.form_submit_button("Apply for API Access"):
            if business_name and email:
                api_key = generate_api_key(business_name, email)
                st.success(f"API Key generated: `{api_key}`")
                st.info("Save this key securely. You will be invoiced monthly based on usage.")
                st.markdown(f"[View API Documentation](https://your-domain.com/api/docs)")
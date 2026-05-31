# services/api_service.py
import streamlit as st
import json
import os
import hashlib
from datetime import datetime, timedelta
from services.i18n import t

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
    st.markdown(f"### 🔌 {t('api_access', 'API Access for Travel Businesses')}")
    st.markdown(t('api_desc', 'Integrate our travel data into your platform'))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"#### 🆓 {t('free_tier', 'Free Tier')}")
        st.markdown(f"- {t('api_free_calls', '100 calls/day')}")
        st.markdown(f"- {t('api_free_data', 'Basic attraction data')}")
        st.markdown(f"- {t('api_free_history', '7-day history')}")
        st.markdown(f"**{t('free', 'Free')}**")
    
    with col2:
        st.markdown(f"#### 💼 {t('business_tier', 'Business Tier')}")
        st.markdown(f"- {t('api_biz_calls', '10,000 calls/month')}")
        st.markdown(f"- {t('api_biz_data', 'Full travel data')}")
        st.markdown(f"- {t('api_biz_history', '1-year history')}")
        st.markdown(f"- {t('api_biz_support', 'Email support')}")
        st.markdown(f"**$99/{t('month', 'month')}**")
    
    with col3:
        st.markdown(f"#### 🏢 {t('enterprise_tier', 'Enterprise Tier')}")
        st.markdown(f"- {t('api_ent_calls', 'Unlimited calls')}")
        st.markdown(f"- {t('api_ent_integration', 'Custom data integration')}")
        st.markdown(f"- {t('api_ent_sla', 'SLA guarantee')}")
        st.markdown(f"- {t('api_ent_support', 'Dedicated support')}")
        st.markdown(f"**{t('custom_pricing', 'Custom pricing')}**")
    
    with st.form("api_request"):
        business_name = st.text_input(t('business_name', 'Business name'))
        email = st.text_input(t('contact_email', 'Contact email'))
        
        if st.form_submit_button(t('apply_api', 'Apply for API Access')):
            if business_name and email:
                api_key = generate_api_key(business_name, email)
                st.success(t('api_key_generated', 'API Key generated: `{key}`').replace('{key}', api_key))
                st.info(t('api_key_save', 'Save this key securely. You will be invoiced monthly based on usage.'))
                st.markdown(f"[{t('api_docs', 'View API Documentation')}](https://your-domain.com/api/docs)")
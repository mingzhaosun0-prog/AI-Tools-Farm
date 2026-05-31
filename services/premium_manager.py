# services/premium_manager.py
import streamlit as st
import json
import os
from datetime import datetime, timedelta
from services.paypal_service import display_premium_paypal, PLANS

PREMIUM_CONFIG_PATH = "config/premium_content.json"
SUBSCRIPTIONS_PATH = "data/subscriptions.json"

def load_premium_content():
    """Load premium content configuration."""
    default_content = {
        "features": {
            "detailed_itineraries": {
                "name": "7-Day Custom Itineraries",
                "description": "AI-powered personalized travel plans",
                "price_monthly": 9.99,
                "price_yearly": 99.99
            },
            "offline_maps": {
                "name": "Offline Maps & Guides",
                "description": "Download maps for offline use",
                "price_monthly": 4.99,
                "price_yearly": 49.99
            },
            "exclusive_deals": {
                "name": "Exclusive Deals",
                "description": "Member-only discounts and promotions",
                "price_monthly": 7.99,
                "price_yearly": 79.99
            },
            "live_support": {
                "name": "24/7 Travel Support",
                "description": "Priority customer service",
                "price_monthly": 14.99,
                "price_yearly": 149.99
            }
        },
        "bundles": {
            "basic": {
                "name": "Basic Plan",
                "features": ["detailed_itineraries"],
                "price_monthly": 9.99,
                "price_yearly": 99.99
            },
            "pro": {
                "name": "Pro Plan",
                "features": ["detailed_itineraries", "offline_maps", "exclusive_deals"],
                "price_monthly": 19.99,
                "price_yearly": 199.99
            },
            "premium": {
                "name": "Premium Plan",
                "features": ["detailed_itineraries", "offline_maps", "exclusive_deals", "live_support"],
                "price_monthly": 29.99,
                "price_yearly": 299.99
            }
        }
    }
    
    if os.path.exists(PREMIUM_CONFIG_PATH):
        with open(PREMIUM_CONFIG_PATH, 'r') as f:
            return json.load(f)
    else:
        os.makedirs(os.path.dirname(PREMIUM_CONFIG_PATH), exist_ok=True)
        with open(PREMIUM_CONFIG_PATH, 'w') as f:
            json.dump(default_content, f, indent=2)
        return default_content

def check_premium_status():
    """Check if user has premium access."""
    if "premium_expiry" not in st.session_state:
        st.session_state["premium_expiry"] = None
        st.session_state["premium_tier"] = None
    
    if st.session_state["premium_expiry"]:
        expiry = datetime.fromisoformat(st.session_state["premium_expiry"])
        if expiry > datetime.now():
            return st.session_state["premium_tier"]
    return None

def display_premium_upgrade():
    """Show premium upgrade options with PayPal checkout."""
    from services.paypal_service import handle_paypal_callback
    handle_paypal_callback()
    
    premium_content = load_premium_content()
    
    st.markdown("### 🌟 Unlock Premium Features")
    st.markdown("Get the most out of your travel planning experience — powered by **PayPal**")
    
    # Display bundles in columns
    bundles = premium_content["bundles"]
    cols = st.columns(len(bundles))
    
    for idx, (bundle_key, bundle) in enumerate(bundles.items()):
        with cols[idx]:
            st.markdown(f"<div style='border:1px solid #e2e8f0;border-radius:1rem;padding:1.2rem;text-align:center;height:100%;'>"
                       f"<h4 style='margin:0 0 0.3rem;'>{bundle['name']}</h4>"
                       f"<div style='font-size:1.8rem;font-weight:700;color:#cc0000;'>${bundle['price_monthly']}</div>"
                       f"<div style='font-size:0.85rem;color:#64748b;'>/month</div>"
                       f"<div style='font-size:0.8rem;color:#94a3b8;margin-bottom:0.8rem;'>"
                       f"or ${bundle['price_yearly']}/year</div>"
                       f"<div style='text-align:left;font-size:0.9rem;margin-bottom:0.8rem;'>"
                       f"<strong>Includes:</strong></div>", unsafe_allow_html=True)
            for feature_key in bundle['features']:
                feature = premium_content['features'][feature_key]
                st.markdown(f"- ✅ {feature['name']}")
            
            # PayPal checkout
            display_premium_paypal(bundle_key, bundle)
            
            st.markdown("</div>", unsafe_allow_html=True)

def protect_premium_content(content_func):
    """Decorator to protect premium content."""
    def wrapper(*args, **kwargs):
        tier = check_premium_status()
        if tier:
            return content_func(*args, **kwargs)
        else:
            st.warning("🔒 This content requires a premium subscription")
            display_premium_upgrade()
            return None
    return wrapper
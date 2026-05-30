# services/premium_manager.py
import streamlit as st
import json
import os
from datetime import datetime, timedelta

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
    """Show premium upgrade options."""
    premium_content = load_premium_content()
    
    st.markdown("### 🌟 Unlock Premium Features")
    st.markdown("Get the most out of your travel planning experience")
    
    # Display bundles in columns
    bundles = premium_content["bundles"]
    cols = st.columns(len(bundles))
    
    for idx, (bundle_key, bundle) in enumerate(bundles.items()):
        with cols[idx]:
            st.markdown(f"#### {bundle['name']}")
            st.markdown(f"**${bundle['price_monthly']}/month**")
            st.markdown(f"or ${bundle['price_yearly']}/year")
            st.markdown("**Includes:**")
            for feature_key in bundle['features']:
                feature = premium_content['features'][feature_key]
                st.markdown(f"- {feature['name']}")
            
            if st.button(f"Upgrade to {bundle['name']}", key=f"upgrade_{bundle_key}"):
                # Simulate payment (in production, integrate Stripe/PayPal)
                st.session_state["premium_tier"] = bundle_key
                st.session_state["premium_expiry"] = (datetime.now() + timedelta(days=30)).isoformat()
                st.success(f"✅ Upgraded to {bundle['name']}! Thank you for your support.")
                st.rerun()

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
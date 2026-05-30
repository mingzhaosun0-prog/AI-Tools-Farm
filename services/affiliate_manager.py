# services/affiliate_manager.py
import streamlit as st
import random
import json
import os
from datetime import datetime

AFFILIATE_CONFIG_PATH = "config/affiliates.json"

# Default affiliate links (replace with your actual affiliate IDs)
DEFAULT_AFFILIATES = {
    "hotels": {
        "booking": "https://www.booking.com/index.html?aid=YOUR_BOOKING_ID",
        "agoda": "https://www.agoda.com/?cid=YOUR_AGODA_ID",
        "trip": "https://www.trip.com/?allianceid=YOUR_TRIP_ID"
    },
    "tours": {
        "viator": "https://www.viator.com/?pid=YOUR_VIATOR_ID",
        "getyourguide": "https://www.getyourguide.com/?partner_id=YOUR_ID",
        "klook": "https://www.klook.com/?aid=YOUR_KLOOK_ID"
    },
    "transport": {
        "train": "https://www.chinahighlights.com/affiliate/",
        "flight": "https://www.ctrip.com/?allianceid=YOUR_ID"
    },
    "travel_insurance": {
        "world_nomads": "https://www.worldnomads.com/?affiliate=YOUR_ID",
        "safetywing": "https://safetywing.com/?referenceID=YOUR_ID"
    }
}

def load_affiliates():
    """Load affiliate configuration from file or create default."""
    if os.path.exists(AFFILIATE_CONFIG_PATH):
        with open(AFFILIATE_CONFIG_PATH, 'r') as f:
            return json.load(f)
    else:
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(AFFILIATE_CONFIG_PATH), exist_ok=True)
        with open(AFFILIATE_CONFIG_PATH, 'w') as f:
            json.dump(DEFAULT_AFFILIATES, f, indent=2)
        return DEFAULT_AFFILIATES

def display_affiliate_sidebar():
    """Display affiliate offers in sidebar."""
    affiliates = load_affiliates()
    
    with st.sidebar:
        st.markdown("### 🏨 Plan Your Trip")
        st.markdown("---")
        
        # Hotel booking
        with st.expander("🏨 Hotels & Accommodation"):
            st.markdown("**Find the best deals:**")
            for name, url in affiliates.get("hotels", {}).items():
                st.markdown(f"- [{name.capitalize()}]({url})")
        
        # Tours & Activities
        with st.expander("🎯 Tours & Activities"):
            for name, url in affiliates.get("tours", {}).items():
                st.markdown(f"- [{name.capitalize()}]({url})")
        
        # Transport
        with st.expander("🚗 Transport"):
            for name, url in affiliates.get("transport", {}).items():
                st.markdown(f"- [{name.capitalize()}]({url})")
        
        # Travel Insurance
        with st.expander("🛡️ Travel Insurance"):
            for name, url in affiliates.get("travel_insurance", {}).items():
                st.markdown(f"- [{name.replace('_', ' ').title()}]({url})")

def display_contextual_affiliate(attraction_name, service_type="hotels"):
    """Display relevant affiliate links based on attraction."""
    affiliates = load_affiliates()
    
    st.markdown("### ✨ Recommended Services")
    st.caption(f"Curated for your visit to {attraction_name}")
    
    cols = st.columns(len(affiliates.get(service_type, {})))
    for idx, (name, url) in enumerate(affiliates.get(service_type, {}).items()):
        with cols[idx]:
            st.markdown(f"[**{name.capitalize()}**]({url})")
            st.caption(f"Book {name} near {attraction_name}")

def track_affiliate_click(affiliate_name, destination):
    """Track affiliate clicks for analytics (optional)."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "affiliate": affiliate_name,
        "destination": destination,
        "ip": st.session_state.get("client_ip", "unknown")
    }
    
    # Append to log file
    log_path = "logs/affiliate_clicks.jsonl"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
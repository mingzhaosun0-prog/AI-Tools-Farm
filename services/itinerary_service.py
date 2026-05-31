# services/itinerary_service.py
import streamlit as st
import json
import os
from datetime import datetime, timedelta
import uuid

ITINERARIES_PATH = "data/custom_itineraries.json"

def init_itinerary_db():
    """Initialize itinerary database."""
    if not os.path.exists(ITINERARIES_PATH):
        os.makedirs(os.path.dirname(ITINERARIES_PATH), exist_ok=True)
        with open(ITINERARIES_PATH, 'w') as f:
            json.dump([], f)

def save_itinerary_request(user_data, itinerary_preferences):
    """Save custom itinerary request."""
    init_itinerary_db()
    
    with open(ITINERARIES_PATH, 'r') as f:
        requests = json.load(f)
    
    new_request = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "user": user_data,
        "preferences": itinerary_preferences,
        "status": "pending",
        "price": calculate_price(itinerary_preferences)
    }
    
    requests.append(new_request)
    
    with open(ITINERARIES_PATH, 'w') as f:
        json.dump(requests, f, indent=2)
    
    return new_request

def calculate_price(preferences):
    """Calculate price based on complexity."""
    base_price = 29
    days = preferences.get("days", 3)
    cities = len(preferences.get("cities", []))
    return base_price + (days * 5) + (cities * 10)

def display_itinerary_builder():
    """Show custom itinerary builder form."""
    st.markdown("### ✈️ Custom Travel Itinerary")
    st.markdown("Get a personalized, detailed day-by-day travel plan")
    
    with st.form("itinerary_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Your name")
            email = st.text_input("Email address")
        with col2:
            days = st.number_input("Number of days", min_value=1, max_value=30, value=5)
            budget = st.selectbox("Budget level", ["Budget ($)", "Moderate ($$)", "Luxury ($$$)"])
        
        destination = st.selectbox(
            "Destination",
            ["Beijing", "Shanghai", "Xi'an", "Chengdu", "Multiple cities"]
        )
        
        interests = st.multiselect(
            "Interests",
            ["History & Culture", "Nature & Scenery", "Food & Dining", 
             "Shopping", "Adventure", "Relaxation", "Photography"]
        )
        
        st.markdown(f"**Estimated price: ${calculate_price({'days': days, 'cities': [destination]})}**")
        st.caption("You'll receive a custom itinerary within 24 hours")
        
        submitted = st.form_submit_button("Request Itinerary")
        
        if submitted and name and email:
            user_data = {"name": name, "email": email}
            preferences = {
                "days": days,
                "budget": budget,
                "destination": destination,
                "interests": interests
            }
            
            request = save_itinerary_request(user_data, preferences)
            st.success(f"✅ Request submitted! (Request ID: {request['id'][:8]})")
            st.info("💳 Complete your payment below to confirm your itinerary:")
            from services.paypal_service import display_itinerary_paypal
            display_itinerary_paypal(request['price'])
# services/ad_manager.py
import streamlit as st
import random
import json
import os

ADS_CONFIG_PATH = "config/sponsored_ads.json"

DEFAULT_ADS = {
    "banner": [
        {
            "title": "Save 20% on Your First Booking!",
            "description": "Use code TRAVEL20 at checkout",
            "link": "https://www.example.com/offer",
            "sponsor": "TravelDeals",
            "display_probability": 0.3
        },
        {
            "title": "eSIM for China Travel",
            "description": "Stay connected with affordable data plans",
            "link": "https://www.example.com/esim",
            "sponsor": "Nomad eSIM",
            "display_probability": 0.25
        }
    ],
    "sidebar": [
        {
            "title": "Pack Smarter with Our Sponsor",
            "description": "Lightweight travel backpacks - 30% off",
            "link": "https://www.example.com/backpacks",
            "sponsor": "TravelGear Pro",
            "display_probability": 0.4
        }
    ],
    "native": [
        {
            "title": "Recommended: Best Time to Visit",
            "description": "Sponsored by Weather.com - Get accurate forecasts",
            "link": "https://www.example.com/weather",
            "sponsor": "WeatherPro",
            "display_probability": 0.2
        }
    ]
}

def load_ads():
    """Load ad configuration."""
    if os.path.exists(ADS_CONFIG_PATH):
        with open(ADS_CONFIG_PATH, 'r') as f:
            return json.load(f)
    else:
        os.makedirs(os.path.dirname(ADS_CONFIG_PATH), exist_ok=True)
        with open(ADS_CONFIG_PATH, 'w') as f:
            json.dump(DEFAULT_ADS, f, indent=2)
        return DEFAULT_ADS

def display_banner_ad():
    """Display a banner ad with probability."""
    ads = load_ads()
    banner_ads = ads.get("banner", [])
    
    # Filter by probability
    eligible_ads = [ad for ad in banner_ads if random.random() < ad.get("display_probability", 0.3)]
    
    if eligible_ads:
        ad = random.choice(eligible_ads)
        with st.container():
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 1rem 0;
                text-align: center;
            ">
                <p style="color: white; margin: 0;">🎯 Sponsored</p>
                <h4 style="color: white; margin: 0.5rem 0;">{ad['title']}</h4>
                <p style="color: #f0f0f0; margin: 0.5rem 0;">{ad['description']}</p>
                <a href="{ad['link']}" target="_blank" style="
                    background: white;
                    color: #667eea;
                    padding: 0.5rem 1rem;
                    border-radius: 2rem;
                    text-decoration: none;
                    display: inline-block;
                    margin-top: 0.5rem;
                ">Learn More →</a>
                <p style="color: #ddd; font-size: 0.7rem; margin-top: 0.5rem;">Presented by {ad['sponsor']}</p>
            </div>
            """, unsafe_allow_html=True)

def display_sidebar_ad():
    """Display ad in sidebar."""
    ads = load_ads()
    sidebar_ads = ads.get("sidebar", [])
    
    eligible_ads = [ad for ad in sidebar_ads if random.random() < ad.get("display_probability", 0.3)]
    
    if eligible_ads:
        ad = random.choice(eligible_ads)
        st.markdown("---")
        st.markdown(f"#### {ad['title']}")
        st.markdown(ad['description'])
        st.markdown(f"[Click here]({ad['link']})")
        st.caption(f"Sponsored by {ad['sponsor']}")

def display_native_ad():
    """Display native ad that blends with content."""
    ads = load_ads()
    native_ads = ads.get("native", [])
    
    eligible_ads = [ad for ad in native_ads if random.random() < ad.get("display_probability", 0.2)]
    
    if eligible_ads:
        ad = random.choice(eligible_ads)
        st.info(f"💡 {ad['title']} - {ad['description']} [Sponsored]({ad['link']})")
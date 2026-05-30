import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageEnhance, ImageOps
import random
import io
from collections import Counter
import re

from services.data_viz import data_visualizer
from services.text_analyzer import text_analyzer
from services.image_processor import image_processor
from services.quote_gen import quote_generator
from services.calculator import smart_calculator
from services.china_guide import china_guide
# Import monetization modules
from services.affiliate_manager import display_affiliate_sidebar, track_affiliate_click
from services.ad_manager import display_banner_ad, display_sidebar_ad
from services.premium_manager import check_premium_status, display_premium_upgrade
from services.itinerary_service import display_itinerary_builder
from services.api_service import display_api_offering
from services.donation import display_donation_support


# ---------------------- Page Configuration ----------------------
st.set_page_config(
    page_title="App Framework | Card Hub",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- Custom CSS for Cards and Styling ----------------------
st.markdown("""
<style>
    /* Card styling */
    .card {
        background-color: #ffffff;
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.1);
        border-color: #cbd5e1;
    }
    .card-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .card-desc {
        color: #4b5563;
        margin-bottom: 1.2rem;
        line-height: 1.4;
    }
    /* Button styling inside card */
    .stButton button {
        width: 100%;
        border-radius: 2rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton button:hover {
        transform: scale(1.02);
    }
    /* Main header */
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1rem;
        color: #6c757d;
        border-top: 1px solid #dee2e6;
    }
    /* Sidebar styling */
    .css-1d391kg, .css-12oz5g7 {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------- Helper Functions for Each App ----------------------

def show_home():
    """Display the home page with all app cards in a responsive grid."""
    st.markdown("""
    <div class="main-header">
        <h1>🧩 App Framework Hub</h1>
        <p>Your modular workspace — each card opens a dedicated mini-app</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Define app cards: (id, title, icon, description)
    apps = [
        ("china_guide", "China Travel Guide", "🇨🇳", "Explore travel guides for each province – attractions, culture & tips."),
        ("data_viz", "Data Visualizer", "📊", "Upload CSV/Excel & create interactive plots (line, bar, scatter)."),
        ("text_analyzer", "Text Analyzer", "✍️", "Word count, character stats, and most frequent words."),
        ("image_processor", "Image Processor", "🖼️", "Adjust brightness, convert to grayscale, apply filters."),
        ("quote_gen", "Quote Generator", "💬", "Get random inspirational quotes to brighten your day."),
        ("calculator", "Smart Calculator", "🧮", "Basic arithmetic with expression evaluation and history."),        
    ]
    
    # Display cards in rows of 3
    cols_per_row = 3
    for i in range(0, len(apps), cols_per_row):
        cols = st.columns(cols_per_row)
        for col_idx, col in enumerate(cols):
            app_idx = i + col_idx
            if app_idx < len(apps):
                app_id, title, icon, desc = apps[app_idx]   # FIX: unpack 4 values, no trailing _
                with col:
                    st.markdown(f"""
                    <div class="card">
                        <div class="card-title">
                            <span style="font-size:2rem;">{icon}</span> {title}
                        </div>
                        <div class="card-desc">{desc}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Launch {title}", key=f"btn_{app_id}", use_container_width=True):
                        st.session_state["current_app"] = app_id
                        st.rerun()


def business_page():
    """Monetization and business opportunities page."""
    st.markdown("<h1 style='text-align: center;'>💼 Business Opportunities</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Advertise", "🔌 API Access", "✈️ Custom Itineraries", "🤝 Partnerships"])
    
    with tab1:
        st.markdown("## Advertise With Us")
        st.markdown("Reach thousands of travel enthusiasts")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Banner Ads**")
            st.markdown("- $500/month")
            st.markdown("- 100k impressions guaranteed")
            st.markdown("- Click tracking included")
        
        with col2:
            st.markdown("**Sponsored Content**")
            st.markdown("- $1000/post")
            st.markdown("- Native integration")
            st.markdown("- Social media promotion")
        
        if st.button("Contact Sales for Advertising"):
            st.info("📧 Email: advertising@travelguide.com")
    
    with tab2:
        display_api_offering()
    
    with tab3:
        st.markdown("## Custom Itineraries for Your Clients")
        st.markdown("White-label travel planning for travel agencies")
        if st.button("Become a Partner Agency"):
            st.info("📧 Email: partnerships@travelguide.com")
    
    with tab4:
        st.markdown("## Strategic Partnerships")
        st.markdown("We're looking for:")
        st.markdown("- Hotel booking platforms")
        st.markdown("- Tour operators")
        st.markdown("- Travel insurance providers")
        st.markdown("- Language learning services")
        
        with st.form("partnership"):
            company = st.text_input("Company name")
            contact = st.text_input("Contact email")
            partnership_type = st.selectbox("Partnership type", ["Affiliate", "API Integration", "White-label", "Strategic"])
            
            if st.form_submit_button("Submit Partnership Inquiry"):
                st.success(f"Thank you {company}! We'll contact you within 48 hours.")

# ---------------------- Main Routing Logic ----------------------
def main():
    # Initialize session state for current app (default: home)
    if "current_app" not in st.session_state:
        st.session_state["current_app"] = "home"
    
    # Routing map
    app_map = {
        "home": show_home,
        "china_guide": china_travel_guide,        
        "data_viz": data_visualizer,
        "text_analyzer": text_analyzer,
        "image_processor": image_processor,
        "quote_gen": quote_generator,
        "calculator": smart_calculator,
        "business": business_page,
    }
    
    # Sidebar always visible for quick navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        st.markdown("---")
        if st.button("🏠 Home", use_container_width=True):
            st.session_state["current_app"] = "home"
            st.rerun()
        st.divider()
        st.markdown("#### 📱 Apps")
        cols_side = st.columns(2)
        apps_list = [
            ("🇨🇳 China Guide", "china_guide"),
            ("📊 Data Viz", "data_viz"),
            ("✍️ Text", "text_analyzer"),
            ("🖼️ Image", "image_processor"),
            ("💬 Quotes", "quote_gen"),
            ("🧮 Calc", "calculator"),
            ("💼 For Business", "business")
        ]
        
        for i, (name, app_id) in enumerate(apps_list):
            if st.button(name, key=f"side_{app_id}", use_container_width=True):
                st.session_state["current_app"] = app_id
                st.rerun()
        st.divider()
        st.caption("✨ Expandable framework — add your own cards by editing the `apps` list in code.")

        # Add monetization elements
        st.divider()
        display_sidebar_ad()  # Display sponsored ads
        
        st.divider()
        st.markdown("### 💰 Support Us")
        if st.button("☕ Buy Me a Coffee", use_container_width=True):
            display_donation_support()
        
        # Display affiliate offers
        display_affiliate_sidebar()
    
    # Render the selected app
    current = st.session_state["current_app"]
    if current in app_map:
        app_map[current]()
    else:
        st.error("App not found. Returning home.")
        st.session_state["current_app"] = "home"
        st.rerun()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>⚡ Streamlit App Framework | Modular Card Design | Easily add new apps</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
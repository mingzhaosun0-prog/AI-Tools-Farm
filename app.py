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
from services.qr_generator import qr_generator
from services.converter import converter
from services.china_guide import china_travel_guide, show_spot_detail
# Import monetization modules
from services.affiliate_manager import display_affiliate_sidebar, track_affiliate_click
from services.ad_manager import display_banner_ad, display_sidebar_ad
from services.premium_manager import check_premium_status, display_premium_upgrade
from services.itinerary_service import display_itinerary_builder
from services.api_service import display_api_offering
from services.donation import display_donation_support


# ---------------------- Page Configuration ----------------------
st.set_page_config(
    page_title="🧩 App Framework Hub | China Travel Guide & Tools",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- SEO Meta Tags ----------------------
st.markdown("""
<meta property="og:title" content="🧩 App Framework Hub — China Travel Guide & Tools">
<meta property="og:description" content="Beijing travel guides, QR code generator, unit converter, data visualization & more.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://ai-tools-farm-ppu2fwjsemrjc6loj8j3m7.streamlit.app/">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="🧩 App Framework Hub">
<meta name="twitter:description" content="Beijing travel guides, QR codes, unit converter & interactive tools.">
<meta name="robots" content="index, follow">
""", unsafe_allow_html=True)

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
    .site-footer {
        margin-top: 4rem;
        padding: 0;
        border-top: 1px solid #e2e8f0;
        font-size: 0.9rem;
    }
    .footer-main {
        background: #f8fafc;
        padding: 2.5rem 2rem 1.5rem;
    }
    .footer-grid {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        gap: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    .footer-col {
        flex: 1 1 180px;
        min-width: 140px;
    }
    .footer-col h4 {
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #1e293b;
        margin: 0 0 0.8rem 0;
    }
    .footer-col ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .footer-col ul li {
        margin-bottom: 0.4rem;
    }
    .footer-col ul li a {
        color: #64748b;
        text-decoration: none;
        transition: color 0.15s;
        cursor: pointer;
    }
    .footer-col ul li a:hover {
        color: #1e3c72;
        text-decoration: underline;
    }
    .footer-brand {
        flex: 2 1 280px;
    }
    .footer-brand h3 {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1e3c72;
        margin: 0 0 0.3rem 0;
    }
    .footer-brand p {
        color: #64748b;
        margin: 0 0 0.8rem 0;
        font-size: 0.85rem;
        line-height: 1.5;
    }
    .footer-social {
        display: flex;
        gap: 0.6rem;
        margin-top: 0.5rem;
    }
    .footer-social a {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background: #e2e8f0;
        color: #475569;
        text-decoration: none;
        font-size: 1rem;
        transition: all 0.2s;
        cursor: pointer;
    }
    .footer-social a:hover {
        background: #1e3c72;
        color: #fff;
        transform: translateY(-2px);
    }
    .footer-bottom {
        background: #f1f5f9;
        padding: 1rem 2rem;
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        border-top: 1px solid #e2e8f0;
    }
    .footer-bottom a {
        color: #64748b;
        text-decoration: none;
    }
    .footer-bottom a:hover {
        color: #1e3c72;
        text-decoration: underline;
    }
    .footer-bottom .dot {
        margin: 0 0.5rem;
        color: #cbd5e1;
    }
    /* Sidebar styling */
    .css-1d391kg, .css-12oz5g7 {
        background-color: #f8f9fa;
    }

    /* ── Travel Guide Styles ── */

    /* Stat cards */
    .stat-card {
        background: white;
        border-radius: 1rem;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e9ecef;
        transition: transform 0.2s;
    }
    .stat-card:hover { transform: translateY(-3px); }
    .stat-num { font-size: 2rem; font-weight: 700; color: #1e3c72; }
    .stat-label { font-size: 0.85rem; color: #6b7280; margin-top: 0.2rem; }

    /* Attraction cards */
    .attraction-card {
        background: white;
        border-radius: 1.2rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        transition: all 0.25s ease;
    }
    .attraction-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 28px rgba(0,0,0,0.1);
        border-color: #2a5298;
    }
    .attraction-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .attraction-card-header h3 {
        margin: 0;
        font-size: 1.4rem;
        color: #1e293b;
    }
    .attraction-subtitle {
        color: #64748b;
        margin: 0.3rem 0 0.8rem;
        font-size: 0.95rem;
    }
    .attraction-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 0.6rem;
        font-size: 0.9rem;
        color: #475569;
    }
    .attraction-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .tag {
        background: #f1f5f9;
        padding: 0.2rem 0.7rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        color: #334155;
        border: 1px solid #e2e8f0;
    }

    /* Info badges on detail page */
    .info-badge {
        background: white;
        border-radius: 0.8rem;
        padding: 0.8rem 0.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #e9ecef;
        height: 100%;
    }
    .badge-icon { font-size: 1.5rem; }
    .badge-label { font-size: 0.7rem; color: #94a3b8; margin-top: 0.1rem; }
    .badge-value { font-size: 0.8rem; font-weight: 600; color: #1e293b; margin-top: 0.15rem; }
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
        ("china_guide", "China Travel Guide", "🇨🇳", "Discover Beijing's top attractions with rich guides, cost calculators, section comparisons & interactive planning tools."),
        ("qr_generator", "QR Code Generator", "📱", "Create custom QR codes with colour picker & download."),
        ("converter", "Unit Converter", "📐", "Convert between 50+ units: length, weight, temperature, volume, speed & data."),
        ("data_viz", "Data Visualizer", "📊", "Upload CSV/Excel & create interactive plots (line, bar, scatter)."),
        ("image_processor", "Image Processor", "🖼️", "Adjust brightness, grayscale, flip, rotate & download."),
        ("text_analyzer", "Text Analyzer", "✍️", "Word count, character stats, and most frequent words."),
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
                        if app_id == "china_guide":
                            st.session_state["beijing_view"] = "list"
                            st.session_state["selected_spot_slug"] = None
                            st.session_state["full_mode_spot"] = None
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
        "qr_generator": qr_generator,
        "converter": converter,
        "data_viz": data_visualizer,
        "image_processor": image_processor,
        "text_analyzer": text_analyzer,
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
            ("� QR Code", "qr_generator"),
            ("📐 Converter", "converter"),
            ("📊 Data Viz", "data_viz"),
            ("🖼️ Image", "image_processor"),
            ("✍️ Text", "text_analyzer"),
            ("💼 For Business", "business")
        ]
        
        for i, (name, app_id) in enumerate(apps_list):
            if st.button(name, key=f"side_{app_id}", use_container_width=True):
                st.session_state["current_app"] = app_id
                # Reset travel guide state when entering
                if app_id == "china_guide":
                    st.session_state["beijing_view"] = "list"
                    st.session_state["selected_spot_slug"] = None
                    st.session_state["full_mode_spot"] = None
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
    <div class="site-footer">
        <div class="footer-main">
            <div class="footer-grid">
                <div class="footer-col footer-brand">
                    <h3>🧩 App Framework Hub</h3>
                    <p>A modular workspace for travel guides, data visualization, image processing, and more. Build, explore, and create with our growing collection of mini-apps.</p>
                    <div class="footer-social">
                        <a href="#" title="GitHub">⌨</a>
                        <a href="#" title="Twitter">𝕏</a>
                        <a href="#" title="YouTube">▶</a>
                        <a href="#" title="Email">✉</a>
                    </div>
                </div>
                <div class="footer-col">
                    <h4>Apps</h4>
                    <ul>
                        <li><a href="#" onclick="return false">🇨🇳 China Guide</a></li>
                        <li><a href="#" onclick="return false">� QR Code Generator</a></li>
                        <li><a href="#" onclick="return false">📐 Unit Converter</a></li>
                        <li><a href="#" onclick="return false">📊 Data Viz</a></li>
                        <li><a href="#" onclick="return false">🖼️ Image Processor</a></li>
                        <li><a href="#" onclick="return false">✍️ Text Analyzer</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Resources</h4>
                    <ul>
                        <li><a href="#" onclick="return false">📖 Documentation</a></li>
                        <li><a href="#" onclick="return false">💻 GitHub Repo</a></li>
                        <li><a href="#" onclick="return false">🐛 Report Issue</a></li>
                        <li><a href="#" onclick="return false">⭐ Request Feature</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Company</h4>
                    <ul>
                        <li><a href="#" onclick="return false">📧 Contact Us</a></li>
                        <li><a href="#" onclick="return false">🔒 Privacy Policy</a></li>
                        <li><a href="#" onclick="return false">📄 Terms of Service</a></li>
                        <li><a href="#" onclick="return false">💼 For Business</a></li>
                    </ul>
                </div>
            </div>
        </div>
        <div class="footer-bottom">
            © 2026 <a href="#">App Framework Hub</a>
            <span class="dot">•</span>
            Built with <a href="https://streamlit.io" target="_blank">Streamlit</a>
            <span class="dot">•</span>
            All rights reserved
            <span class="dot">•</span>
            v2.0.0
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
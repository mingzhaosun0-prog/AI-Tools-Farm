import streamlit as st
import yaml
import os
import glob
import json
import random
from datetime import datetime

from services.china_guide import china_travel_guide, show_spot_detail
# Import monetization modules
from services.affiliate_manager import display_affiliate_sidebar, track_affiliate_click
from services.ad_manager import display_banner_ad, display_sidebar_ad
from services.premium_manager import check_premium_status, display_premium_upgrade
from services.itinerary_service import display_itinerary_builder
from services.api_service import display_api_offering
from services.donation import display_donation_support
# Import i18n
from services.i18n import init_language, get_language, set_language, t, render_language_switcher, get_language_badge


# ---------------------- Page Configuration ----------------------
st.set_page_config(
    page_title="🇨🇳 China Travel Guide | Explore Beijing, Shanghai & Beyond",
    page_icon="🇨🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- Data Paths ----------------------
TRAVEL_DATA_DIR = os.path.join(os.path.dirname(__file__), "travel", "data")

@st.cache_data
def load_city_attractions(city: str) -> dict:
    """Load all YAML attraction files for a given city."""
    city_dir = os.path.join(TRAVEL_DATA_DIR, city)
    attractions = {}
    if not os.path.isdir(city_dir):
        return attractions
    for yaml_file in glob.glob(os.path.join(city_dir, "*.yaml")):
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data and "name" in data:
                slug = os.path.splitext(os.path.basename(yaml_file))[0]
                data["_slug"] = slug
                attractions[slug] = data
    return attractions

# ---------------------- SEO Meta Tags ----------------------
st.markdown("""
<meta property="og:title" content="🇨🇳 China Travel Guide — Beijing, Shanghai & Beyond">
<meta property="og:description" content="Comprehensive China travel guides with interactive planners, cost calculators, section comparisons, seasonal tips & more.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://ai-tools-farm-ppu2fwjsemrjc6loj8j3m7.streamlit.app/">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="🇨🇳 China Travel Guide">
<meta name="twitter:description" content="Comprehensive China travel guides with interactive planning tools.">
<meta name="robots" content="index, follow">
""", unsafe_allow_html=True)

# ---------------------- China Travel Theme CSS ----------------------
st.markdown("""
<style>
    /* ── Global ── */
    #root > div:nth-child(1) > div > div > div > div > div > div {
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    .stApp {
        background: #fafbfc;
    }

    /* ── City Hero ── */
    .city-hero {
        background: linear-gradient(135deg, #8B0000 0%, #CC0000 30%, #1e3c72 70%, #0f1f3d 100%);
        padding: 2.5rem 2rem;
        border-radius: 1.5rem;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
    }
    .city-hero::before {
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(255,215,0,0.08) 0%, transparent 50%);
        pointer-events: none;
    }
    .city-hero h1 { margin: 0; font-size: 2.8rem; position: relative; }
    .city-hero h1 span.gold { color: #ffd700; }
    .city-hero p { margin: 0.5rem 0 0; font-size: 1.15rem; opacity: 0.9; }
    .season-badge {
        display: inline-block;
        margin-top: 1rem;
        background: rgba(255,255,255,0.15);
        padding: 0.5rem 1.5rem;
        border-radius: 2rem;
        font-size: 0.95rem;
        backdrop-filter: blur(4px);
    }

    /* ── Stat Cards ── */
    .stat-card {
        background: white;
        border-radius: 1rem;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e9ecef;
        transition: transform 0.2s;
    }
    .stat-card:hover { transform: translateY(-3px); border-color: #cc0000; }
    .stat-num { font-size: 2rem; font-weight: 700; color: #cc0000; }
    .stat-label { font-size: 0.85rem; color: #6b7280; margin-top: 0.2rem; }

    /* ── Attraction Cards ── */
    .attraction-card {
        background: white;
        border-radius: 1.2rem;
        overflow: hidden;
        margin: 1rem 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        transition: all 0.25s ease;
    }
    .attraction-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 28px rgba(0,0,0,0.1);
        border-color: #cc0000;
    }
    .attraction-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
        padding: 1.5rem 1.5rem 0;
    }
    .attraction-card-header h3 {
        margin: 0;
        font-size: 1.4rem;
        color: #1e293b;
    }
    .attraction-subtitle {
        color: #64748b;
        margin: 0.3rem 1.5rem 0.8rem;
        font-size: 0.95rem;
    }
    .attraction-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin: 0 1.5rem 0.6rem;
        font-size: 0.9rem;
        color: #475569;
    }
    .attraction-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        padding: 0 1.5rem 1rem;
    }
    .tag {
        background: #f1f5f9;
        padding: 0.2rem 0.7rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        color: #334155;
        border: 1px solid #e2e8f0;
    }

    /* ── Info Badges (detail page) ── */
    .info-badge {
        background: white;
        border-radius: 0.8rem;
        padding: 0.8rem 0.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #e9ecef;
        height: 100%;
        transition: border-color 0.2s;
    }
    .info-badge:hover { border-color: #cc0000; }
    .badge-icon { font-size: 1.5rem; }
    .badge-label { font-size: 0.7rem; color: #94a3b8; margin-top: 0.1rem; }
    .badge-value { font-size: 0.8rem; font-weight: 600; color: #1e293b; margin-top: 0.15rem; }

    /* ── Buttons ── */
    .stButton button {
        width: 100%;
        border-radius: 2rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton button:hover {
        transform: scale(1.02);
    }
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, #cc0000, #8B0000);
        border: none;
        color: white;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        background: linear-gradient(135deg, #e00000, #a00000);
        color: white;
    }

    /* ── Sidebar ── */
    .css-1d391kg, section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #fff 100%);
    }
    section[data-testid="stSidebar"] hr {
        border-color: #e9ecef;
    }

    /* ── Footer ── */
    .site-footer {
        margin-top: 4rem;
        padding: 0;
        border-top: 1px solid #e2e8f0;
        font-size: 0.9rem;
    }
    .footer-main {
        background: linear-gradient(135deg, #1e3c72, #0f1f3d);
        padding: 2.5rem 2rem 1.5rem;
        color: #cbd5e1;
    }
    .footer-grid {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        gap: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    .footer-col { flex: 1 1 180px; min-width: 140px; }
    .footer-col h4 {
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #f1f5f9;
        margin: 0 0 0.8rem 0;
    }
    .footer-col ul { list-style: none; padding: 0; margin: 0; }
    .footer-col ul li { margin-bottom: 0.4rem; }
    .footer-col ul li a { color: #94a3b8; text-decoration: none; transition: color 0.15s; cursor: pointer; }
    .footer-col ul li a:hover { color: #ffd700; text-decoration: underline; }
    .footer-brand { flex: 2 1 280px; }
    .footer-brand h3 { font-size: 1.3rem; font-weight: 700; color: #ffd700; margin: 0 0 0.3rem 0; }
    .footer-brand p { color: #94a3b8; margin: 0 0 0.8rem 0; font-size: 0.85rem; line-height: 1.5; }
    .footer-social { display: flex; gap: 0.6rem; margin-top: 0.5rem; }
    .footer-social a {
        display: inline-flex; align-items: center; justify-content: center;
        width: 34px; height: 34px; border-radius: 50%;
        background: rgba(255,255,255,0.1); color: #94a3b8;
        text-decoration: none; font-size: 1rem;
        transition: all 0.2s; cursor: pointer;
    }
    .footer-social a:hover { background: #ffd700; color: #1e3c72; transform: translateY(-2px); }
    .footer-bottom {
        background: #0a1628;
        padding: 1.2rem 2rem;
        text-align: center;
        color: #64748b;
        font-size: 0.8rem;
        border-top: 1px solid rgba(255,255,255,0.05);
    }
    .footer-bottom a {
        color: #94a3b8;
        text-decoration: none;
        transition: color 0.2s;
    }
    .footer-bottom a:hover {
        color: #ffd700;
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------- Helper Functions for Each App ----------------------

def _weather_tip():
    month = datetime.now().month
    if 3 <= month <= 5:
        return "🌸", "Spring", "Mild and pleasant — perfect for sightseeing!"
    elif 6 <= month <= 8:
        return "☀️", "Summer", "Hot & humid — plan indoor mornings, stay hydrated."
    elif 9 <= month <= 11:
        return "🍂", "Autumn", "Crisp air, golden foliage — the best season."
    else:
        return "❄️", "Winter", "Cold but fewer crowds — bundle up and enjoy!"


def show_home():
    """China Travel Portal — home page with city explorer and tools."""
    season_icon, season_name, season_desc = _weather_tip()
    cities_available = [d for d in os.listdir(TRAVEL_DATA_DIR)
                        if os.path.isdir(os.path.join(TRAVEL_DATA_DIR, d)) and not d.startswith("_")]

    total_attractions = sum(len(load_city_attractions(c)) for c in cities_available)

    # ── Hero ──
    st.markdown(f"""
    <div class="city-hero">
        <h1>🇨🇳 <span class="gold">China</span> Travel Guide</h1>
        <p>Expert guides, interactive planners & curated tips for {', '.join(c.title() for c in cities_available)}</p>
        <div class="season-badge">{season_icon} <strong>{season_name}</strong> — {season_desc}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats Row ──
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.markdown(f"<div class='stat-card'><div class='stat-num'>{len(cities_available)}</div><div class='stat-label'>Cities</div></div>", unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"<div class='stat-card'><div class='stat-num'>{total_attractions}</div><div class='stat-label'>Attractions</div></div>", unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"<div class='stat-card'><div class='stat-num'>🌏</div><div class='stat-label'>UNESCO Sites</div></div>", unsafe_allow_html=True)
    with col_s4:
        st.markdown(f"<div class='stat-card'><div class='stat-num'>🧭</div><div class='stat-label'>Plan Your Trip</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    # ── City Quick-Start ──
    st.markdown("<h2 style='text-align:center;'>🏛️ Explore a City</h2>", unsafe_allow_html=True)
    city_cols = st.columns(len(cities_available))
    for idx, city_name in enumerate(cities_available):
        with city_cols[idx]:
            city_display = city_name.title()
            attrs = load_city_attractions(city_name)
            emoji = "🏯" if city_name == "beijing" else "🌉" if city_name == "shanghai" else "🏛️"
            names_list = "\n".join(f"• {a['name']}" for a in list(attrs.values())[:4])
            st.markdown(f"""
            <div class='attraction-card' style='text-align:center;padding:1.5rem;'>
                <div style='font-size:3rem;'>{emoji}</div>
                <h3 style='margin:0.5rem 0 0;'>{city_display}</h3>
                <p style='color:#64748b;font-size:0.9rem;margin:0.3rem 0 0.8rem;'>{len(attrs)} attractions</p>
                <div style='font-size:0.85rem;color:#475569;text-align:left;padding:0 0.5rem;'>
                    {names_list}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🇨🇳 Explore {city_display}", key=f"home_city_{city_name}", use_container_width=True):
                st.session_state["current_app"] = "china_guide"
                st.session_state["beijing_view"] = "list"
                st.session_state["selected_spot_slug"] = None
                st.session_state["full_mode_spot"] = None
                st.session_state["travel_city_selector"] = city_name
                st.rerun()

    st.markdown("---")

    # ── Features Section ──
    st.markdown("<h2 style='text-align:center;'>✨ Travel Tools</h2>", unsafe_allow_html=True)
    tools_cols = st.columns(3)
    tools = [
        ("🗓️", "Plan My Day", "Build an optimised itinerary with cost estimates"),
        ("⚖️", "Compare Attractions", "Side-by-side comparison of ratings, prices & sections"),
        ("💰", "Cost Calculator", "Estimate your total trip budget per attraction"),
        ("📸", "Photo Gallery", "Browse high-quality images of each attraction"),
        ("🚇", "Getting Around", "Metro, taxi, bike & bus guides for each city"),
        ("🌿", "Seasonal Tips", "Best times to visit based on weather & crowds"),
    ]
    for i, (icon, title, desc) in enumerate(tools):
        with tools_cols[i % 3]:
            st.markdown(f"""
            <div class='attraction-card' style='text-align:center;padding:1.2rem;'>
                <div style='font-size:2.5rem;'>{icon}</div>
                <h4 style='margin:0.3rem 0 0;font-size:1.1rem;'>{title}</h4>
                <p style='color:#64748b;font-size:0.85rem;margin:0.3rem 0 0;'>{desc}</p>
            </div>
            """, unsafe_allow_html=True)


def business_page():
    """Monetization and business opportunities page."""
    st.markdown(f"<h1 style='text-align: center;'>💼 {t('business_opportunities')}</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs([f"📈 {t('advertise')}", f"🔌 {t('api_access')}", f"✈️ {t('custom_itineraries')}", f"🤝 {t('partnerships')}"])
    
    with tab1:
        st.markdown(f"## {t('advertise_with_us')}")
        st.markdown(t('reach_travelers'))
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{t('banner_ads')}**")
            st.markdown("- $500/month")
            st.markdown("- 100k impressions guaranteed")
            st.markdown("- Click tracking included")
        
        with col2:
            st.markdown(f"**{t('sponsored_content')}**")
            st.markdown("- $1000/post")
            st.markdown("- Native integration")
            st.markdown("- Social media promotion")
        
        if st.button(t('contact_sales')):
            st.info(f"📧 {t('email')}: advertising@travelguide.com")
    
    with tab2:
        display_api_offering()
    
    with tab3:
        st.markdown(f"## {t('custom_itineraries_title')}")
        st.markdown(t('white_label'))
        if st.button(t('become_partner')):
            st.info(f"📧 {t('email')}: partnerships@travelguide.com")
    
    with tab4:
        st.markdown(f"## {t('strategic_partnerships')}")
        st.markdown(t('looking_for'))
        st.markdown(f"- {t('hotel_platforms')}")
        st.markdown(f"- {t('tour_operators')}")
        st.markdown(f"- {t('travel_insurance')}")
        st.markdown(f"- {t('language_services')}")
        
        with st.form("partnership"):
            company = st.text_input(t('company_name'))
            contact = st.text_input(t('contact_email'))
            partnership_type = st.selectbox(t('partnership_type'), [t('affiliate'), t('api_integration'), t('white_label_option'), t('strategic')])
            
            if st.form_submit_button(t('submit')):
                st.success(f"{t('thank_you')} {company}! {t('contact_within_48h')}")

# ---------------------- Main Routing Logic ----------------------
def main():
    # Initialize language system
    init_language()
    
    # Initialize session state
    if "current_app" not in st.session_state:
        st.session_state["current_app"] = "home"
    
    # Routing map — only China travel tools
    app_map = {
        "home": show_home,
        "china_guide": china_travel_guide,
        "business": business_page,
    }
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:0.5rem 0;'>
            <span style='font-size:2.5rem;'>🇨🇳</span>
            <h3 style='margin:0.2rem 0 0;color:#cc0000;'>China Travel</h3>
            <p style='font-size:0.8rem;color:#94a3b8;margin:0;'>Beijing · Shanghai</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Language switcher
        render_language_switcher()
        st.markdown("---")
        
        if st.button(f"🏠 {t('home')}", use_container_width=True):
            st.session_state["current_app"] = "home"
            st.rerun()
        if st.button(f"🇨🇳 {t('china_guide')}", use_container_width=True):
            st.session_state["current_app"] = "china_guide"
            st.session_state["beijing_view"] = "list"
            st.session_state["selected_spot_slug"] = None
            st.session_state["full_mode_spot"] = None
            st.rerun()
        if st.button(f"💼 {t('business')}", use_container_width=True):
            st.session_state["current_app"] = "business"
            st.rerun()
        
        st.divider()
        
        # Quick city jump
        st.markdown(f"#### 🏛️ {t('quick_city', 'Quick City')}")
        cities_list = [d for d in os.listdir(TRAVEL_DATA_DIR)
                       if os.path.isdir(os.path.join(TRAVEL_DATA_DIR, d)) and not d.startswith("_")]
        for city_name in cities_list:
            emoji = "🏯" if city_name == "beijing" else "🌉"
            if st.button(f"{emoji} {city_name.title()}", key=f"qc_{city_name}", use_container_width=True):
                st.session_state["current_app"] = "china_guide"
                st.session_state["beijing_view"] = "list"
                st.session_state["selected_spot_slug"] = None
                st.session_state["full_mode_spot"] = None
                st.session_state["travel_city_selector"] = city_name
                st.rerun()
        
        st.divider()
        
        # Monetization
        display_sidebar_ad()
        
        st.divider()
        st.markdown(f"### ☕ {t('support_us')}")
        if st.button(f"☕ {t('buy_coffee')}", use_container_width=True):
            display_donation_support()
        
        display_affiliate_sidebar()
    
    # Render
    current = st.session_state["current_app"]
    if current in app_map:
        app_map[current]()
    else:
        st.session_state["current_app"] = "home"
        st.rerun()
    
    # ── Footer ──
    total_cities_list = [d for d in os.listdir(TRAVEL_DATA_DIR)
                         if os.path.isdir(os.path.join(TRAVEL_DATA_DIR, d)) and not d.startswith("_")]
    total_cities = len(total_cities_list)
    total_attrs = sum(len(load_city_attractions(c)) for c in total_cities_list)

    st.markdown(f"""
    <div class="site-footer">
        <div class="footer-main">
            <div class="footer-grid">
                <div class="footer-col footer-brand" style="flex:3 1 300px;">
                    <h3 style="font-size:1.5rem;font-weight:700;color:#ffd700;margin:0 0 0.3rem 0;">&#127944; China Travel Guide</h3>
                    <p style="color:#94a3b8;margin:0.3rem 0 0.8rem;font-size:0.85rem;line-height:1.6;">
                        Expert guides for Beijing, Shanghai &amp; beyond. Interactive planners, cost calculators, 
                        section comparisons &amp; seasonal tips.
                    </p>
                    <div class="footer-stats" style="display:flex;gap:0.8rem;margin:0.6rem 0 1rem;flex-wrap:wrap;">
                        <div style="background:rgba(255,255,255,0.08);border-radius:0.5rem;padding:0.3rem 0.8rem;text-align:center;min-width:55px;">
                            <div style="font-size:1.1rem;font-weight:700;color:#ffd700;">{total_cities}</div>
                            <div style="font-size:0.6rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.03em;">Cities</div>
                        </div>
                        <div style="background:rgba(255,255,255,0.08);border-radius:0.5rem;padding:0.3rem 0.8rem;text-align:center;min-width:55px;">
                            <div style="font-size:1.1rem;font-weight:700;color:#ffd700;">{total_attrs}</div>
                            <div style="font-size:0.6rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.03em;">Attractions</div>
                        </div>
                        <div style="background:rgba(255,255,255,0.08);border-radius:0.5rem;padding:0.3rem 0.8rem;text-align:center;min-width:55px;">
                            <div style="font-size:1.1rem;font-weight:700;color:#ffd700;">4.9&#9733;</div>
                            <div style="font-size:0.6rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.03em;">Avg Rating</div>
                        </div>
                        <div style="background:rgba(255,255,255,0.08);border-radius:0.5rem;padding:0.3rem 0.8rem;text-align:center;min-width:55px;">
                            <div style="font-size:1.1rem;font-weight:700;color:#ffd700;">{total_cities * 4}</div>
                            <div style="font-size:0.6rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.03em;">Sections</div>
                        </div>
                    </div>
                    <div class="footer-social">
                        <a href="#" title="WeChat">&#128172;</a>
                        <a href="#" title="Weibo">&#120120;</a>
                        <a href="#" title="Travel Blog">&#9999;&#65039;</a>
                        <a href="#" title="Instagram">&#128247;</a>
                        <a href="#" title="YouTube">&#9654;&#65039;</a>
                        <a href="#" title="Email">&#9993;&#65039;</a>
                    </div>
                </div>
                <div class="footer-col">
                    <h4>Cities</h4>
                    <ul>
                        <li><a href="#" onclick="return false">&#127975; Beijing</a></li>
                        <li><a href="#" onclick="return false">&#127753; Shanghai</a></li>
                        <li><a href="#" onclick="return false">&#127963; Xi'an</a></li>
                        <li><a href="#" onclick="return false">&#128060; Chengdu</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Plan</h4>
                    <ul>
                        <li><a href="#" onclick="return false">&#128473;&#65039; Itineraries</a></li>
                        <li><a href="#" onclick="return false">&#128176; Budget</a></li>
                        <li><a href="#" onclick="return false">&#128646; Transport</a></li>
                        <li><a href="#" onclick="return false">&#127800; Seasons</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Business</h4>
                    <ul>
                        <li><a href="#" onclick="return false">&#128200; Advertise</a></li>
                        <li><a href="#" onclick="return false">&#128268; API Access</a></li>
                        <li><a href="#" onclick="return false">&#129309; Partnerships</a></li>
                        <li><a href="#" onclick="return false">&#9992;&#65039; Custom Tours</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>{t('resources')}</h4>
                    <ul>
                        <li><a href="#" onclick="return false">&#128214; {t('documentation')}</a></li>
                        <li><a href="#" onclick="return false">💻 {t('github_repo')}</a></li>
                        <li><a href="#" onclick="return false">🐛 {t('report_issue')}</a></li>
                        <li><a href="#" onclick="return false">⭐ {t('request_feature')}</a></li>
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
            © 2026 <a href="#">{t('app_title')}</a>
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
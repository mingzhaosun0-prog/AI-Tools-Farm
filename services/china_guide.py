import streamlit as st
import yaml
import os
import glob
from datetime import datetime

# ── Data Loading ──────────────────────────────────────────

TRAVEL_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "travel", "data")

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
                # Compute a rating if not present
                if "rating" not in data:
                    data["rating"] = _infer_rating(data)
                attractions[slug] = data
    return attractions

def _infer_rating(spot: dict) -> float:
    """Infer a rating based on data richness (1-5)."""
    score = 3.5
    if spot.get("images"):
        score += 0.5
    if spot.get("sections"):
        score += 0.5
    if spot.get("visiting_guidance"):
        score += 0.5
    if spot.get("history") and len(spot["history"]) > 100:
        score += 0.5
    if spot.get("nearby_attractions"):
        score += 0.3
    if spot.get("average_cost_per_person"):
        score += 0.2
    return min(round(score, 1), 5.0)

def _star_rating(rating: float) -> str:
    full = "★" * int(rating)
    half = "½" if rating % 1 >= 0.3 else ""
    empty = "☆" * (5 - int(rating) - (1 if half else 0))
    return f"<span style='color:#f4b400;'>{full}{half}{empty}</span> <span style='color:#888;font-size:0.85rem;'>({rating})</span>"

def _difficulty_badge(difficulty: str) -> str:
    colors = {"easy": "#22c55e", "moderate": "#eab308", "challenging": "#f97316", "strenuous": "#ef4444"}
    color = colors.get(difficulty.lower().strip(), "#888")
    return f"<span style='background:{color}20;color:{color};padding:2px 10px;border-radius:12px;font-size:0.8rem;font-weight:600;'>{difficulty}</span>"

# ── Travel Helper Utilities ───────────────────────────────

def _weather_tip():
    """Return simple seasonal advice."""
    month = datetime.now().month
    if 3 <= month <= 5:
        return "🌸", "Spring", "Mild and pleasant — perfect for sightseeing! Light jacket recommended."
    elif 6 <= month <= 8:
        return "☀️", "Summer", "Hot & humid (30-35°C). Stay hydrated, wear sun protection, plan indoor mornings."
    elif 9 <= month <= 11:
        return "🍂", "Autumn", "Crisp air, golden foliage — the best season for outdoor attractions."
    else:
        return "❄️", "Winter", "Cold (0-5°C) but fewer crowds. Bundle up and enjoy clear, crisp skies."

# ── Main Entry Point (called from app.py) ─────────────────

def china_travel_guide():
    """China Travel Guide — main page with city selection and attraction overview."""
    # ── Initialize session state ──
    if "beijing_view" not in st.session_state:
        st.session_state["beijing_view"] = "list"
    if "selected_spot_slug" not in st.session_state:
        st.session_state["selected_spot_slug"] = None
    if "full_mode_spot" not in st.session_state:
        st.session_state["full_mode_spot"] = None

    # ── Load data ──
    cities = [d for d in os.listdir(TRAVEL_DATA_DIR)
              if os.path.isdir(os.path.join(TRAVEL_DATA_DIR, d)) and not d.startswith("_")]
    city = st.selectbox("📍 Choose a city", cities, index=0 if "beijing" in cities else 0,
                        key="travel_city_selector")
    attractions = load_city_attractions(city)

    # ── Route: detail view vs list view ──
    if st.session_state["beijing_view"] == "detail" and st.session_state["selected_spot_slug"]:
        slug = st.session_state["selected_spot_slug"]
        if slug in attractions:
            spot = attractions[slug]
            # If full_mode_spot is set, pass full_page=True
            full_mode = st.session_state.get("full_mode_spot") is not None
            show_spot_detail(spot, full_page=full_mode)
            return
        else:
            st.session_state["beijing_view"] = "list"

    # ── Hero section ──
    season_icon, season_name, season_desc = _weather_tip()
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #e74c3c 100%);
        padding: 2.5rem 2rem;
        border-radius: 1.5rem;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
    '>
        <h1 style='margin:0;font-size:2.8rem;'>🇨🇳 China Travel Guide</h1>
        <p style='margin:0.5rem 0 0 0;font-size:1.2rem;opacity:0.9;'>
            Discover ancient wonders, vibrant culture & unforgettable experiences
        </p>
        <div style='margin-top:1rem;display:inline-block;background:rgba(255,255,255,0.15);padding:0.5rem 1.5rem;border-radius:2rem;'>
            {season_icon} <strong>{season_name}</strong> — {season_desc}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not attractions:
        st.info(f"✨ No attractions loaded yet for **{city.title()}**. Add YAML files to `travel/data/{city}/`.")
        return

    # ── Stats banner ──
    total_spots = len(attractions)
    top_rated = max(a.get("rating", 0) for a in attractions.values())
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.markdown(f"<div class='stat-card'><div class='stat-num'>{total_spots}</div><div class='stat-label'>Attractions</div></div>", unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"<div class='stat-card'><div class='stat-num'>{top_rated}★</div><div class='stat-label'>Top Rated</div></div>", unsafe_allow_html=True)
    with col_s3:
        cities_total = len([d for d in os.listdir(TRAVEL_DATA_DIR) if os.path.isdir(os.path.join(TRAVEL_DATA_DIR, d)) and not d.startswith("_")])
        st.markdown(f"<div class='stat-card'><div class='stat-num'>{cities_total}</div><div class='stat-label'>Cities</div></div>", unsafe_allow_html=True)
    with col_s4:
        sections_count = sum(len(a.get("sections", {})) for a in attractions.values())
        st.markdown(f"<div class='stat-card'><div class='stat-num'>{sections_count}</div><div class='stat-label'>Sections</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    # ── Attraction cards ──
    st.markdown(f"<h2>🏛️ Top Attractions in {city.title()}</h2>", unsafe_allow_html=True)

    # Sort by rating descending
    sorted_attractions = sorted(attractions.values(), key=lambda x: x.get("rating", 0), reverse=True)

    for spot in sorted_attractions:
        _render_attraction_card(spot)

    # ── Quick Planning Tools ──
    with st.expander("🧭 Travel Planning Tools", expanded=False):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("#### 📅 Best Times to Visit")
            month = datetime.now().month
            best_months = "April–June & September–October" 
            st.info(f"**Peak season:** {best_months}")
            st.markdown("- ✅ **Spring (Mar–May):** Cherry blossoms, mild weather")
            st.markdown("- ✅ **Autumn (Sep–Nov):** Golden foliage, clear skies")
            st.markdown("- ⚠️ **Summer (Jun–Aug):** Hot but vibrant")
            st.markdown("- ❄️ **Winter (Dec–Feb):** Fewer crowds, cold, possible snow")
        with col_t2:
            st.markdown("#### 🚇 Getting Around Beijing")
            transport_opts = {
                "🚇 Metro": "Fast, cheap (¥3-9), covers all major spots",
                "🚌 Bus": "Extensive network, English signs on key routes",
                "🚕 Taxi": "¥13 flagfall, use apps like Didi",
                "🚲 Bike": "Shared bikes (¥1-2/30min) — great for hutongs"
            }
            for mode, desc in transport_opts.items():
                st.markdown(f"**{mode}** — {desc}")

    # ── Compare attractions ──
    with st.expander("⚖️ Compare Attractions Side-by-Side", expanded=False):
        names = [a["name"] for a in attractions.values()]
        selected = st.multiselect("Select 2-4 attractions to compare", names, default=names[:min(2, len(names))])
        if len(selected) >= 2:
            comp_data = []
            for a in attractions.values():
                if a["name"] in selected:
                    comp_data.append({
                        "Attraction": a["name"],
                        "Rating ★": a.get("rating", "—"),
                        "Ticket (¥)": (a.get("ticket_price", "")[:30] + "…") if a.get("ticket_price") and len(a["ticket_price"]) > 30 else a.get("ticket_price", "—"),
                        "Hours": (a.get("opening_hours", "")[:35] + "…") if a.get("opening_hours") and len(a["opening_hours"]) > 35 else a.get("opening_hours", "—"),
                        "Time Needed": a.get("estimated_time_needed", "—"),
                        "Sections": len(a.get("sections", {})),
                    })
            st.dataframe(comp_data, width="stretch", hide_index=True)
        else:
            st.info("Select at least 2 attractions to compare.")


def _render_attraction_card(spot: dict):
    """Render a single attraction card with rich visuals."""
    rating_html = _star_rating(spot.get("rating", 0))
    sections_count = len(spot.get("sections", {}))

    # Build tag items
    tags = []
    hours = spot.get("opening_hours", "N/A")
    if len(hours) > 35:
        hours = hours[:35] + "…"
    tags.append(f"<span class='tag'>🕒 {hours}</span>")

    if sections_count:
        label = "section" if sections_count == 1 else "sections"
        tags.append(f"<span class='tag'>🗺️ {sections_count} {label}</span>")

    acts = spot.get("activities", "")
    if len(acts) > 30:
        acts = acts[:30] + "…"
    if acts:
        tags.append(f"<span class='tag'>🏞️ {acts}</span>")

    # Truncate ticket price
    ticket = spot.get("ticket_price", "N/A")
    if len(ticket) > 45:
        ticket = ticket[:45] + "…"

    card_html = (
        "<div class='attraction-card'>"
        "<div class='attraction-card-inner'>"
        "<div class='attraction-card-body'>"
        "<div class='attraction-card-header'>"
        f"<h3>{spot['name']}</h3>"
        f"<div>{rating_html}</div>"
        "</div>"
        f"<p class='attraction-subtitle'>{spot.get('subtitle', '')}</p>"
        "<div class='attraction-meta'>"
        f"<span>📍 {spot.get('location', 'N/A')}</span>"
        f"<span>🎟️ {ticket}</span>"
        "</div>"
        "<div class='attraction-tags'>"
        + "".join(tags)
        + "</div></div></div></div>"
    )

    st.markdown(card_html, unsafe_allow_html=True)

    col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
    with col_b1:
        if st.button(f"🔍 View Details — {spot['name']}", key=f"view_{spot['_slug']}", width="stretch"):
            st.session_state["beijing_view"] = "detail"
            st.session_state["selected_spot_slug"] = spot["_slug"]
            st.session_state["full_mode_spot"] = None
            st.rerun()
    with col_b2:
        if st.button(f"🗺️ Full Page", key=f"full_{spot['_slug']}", width="stretch"):
            st.session_state["beijing_view"] = "detail"
            st.session_state["selected_spot_slug"] = spot["_slug"]
            st.session_state["full_mode_spot"] = spot
            st.rerun()
    with col_b3:
        # Quick "add to favorites" toggle
        fav_key = f"fav_{spot['_slug']}"
        if fav_key not in st.session_state:
            st.session_state[fav_key] = False
        if st.button(
            f"{'❤️' if st.session_state[fav_key] else '🤍'} Favourite",
            key=f"fav_btn_{spot['_slug']}",
            width="stretch"
        ):
            st.session_state[fav_key] = not st.session_state[fav_key]
            if st.session_state[fav_key]:
                st.toast(f"⭐ Added **{spot['name']}** to your favourites!", icon="❤️")
            else:
                st.toast(f"Removed **{spot['name']}** from favourites.", icon="💔")


# ── Spot Detail View ──────────────────────────────────────

def show_spot_detail(spot: dict, full_page: bool = False):
    """Display detailed information for a single attraction with rich visuals."""

    rating_html = _star_rating(spot.get("rating", 0))

    # ── Hero header ──
    bg_style = ""
    if spot.get("images"):
        bg_style = f"background: linear-gradient(rgba(0,0,0,0.55),rgba(0,0,0,0.55)), url('{spot['images'][0]['url']}') center/cover;"
    else:
        bg_style = "background: linear-gradient(135deg, #1e3c72, #2a5298);"

    st.markdown(f"""
    <div style='{bg_style} padding: 3rem 2rem 2rem; border-radius: 1.5rem; margin-bottom: 1.5rem; text-align: center; color: white; min-height: 220px; display: flex; flex-direction: column; justify-content: center;'>
        <h1 style='margin:0; font-size:{"2.8rem" if full_page else "2.2rem"};'>{spot['name']}</h1>
        <p style='margin:0.3rem 0 0.5rem;font-size:{"1.3rem" if full_page else "1.1rem"};opacity:0.9;'>{spot.get('subtitle', '')}</p>
        <div>{rating_html}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick info badges ──
    col_badges = st.columns(5)
    badge_data = [
        ("📍", "Location", spot.get("location", "N/A")[:25]),
        ("🕒", "Hours", (spot.get("opening_hours", "")[:20] + "…") if spot.get("opening_hours") and len(spot["opening_hours"]) > 20 else spot.get("opening_hours", "N/A")),
        ("🎟️", "Ticket", (spot.get("ticket_price", "")[:20] + "…") if spot.get("ticket_price") and len(spot["ticket_price"]) > 20 else spot.get("ticket_price", "N/A")),
        ("🌿", "Best Time", (spot.get("best_time", "")[:20] + "…") if spot.get("best_time") and len(spot["best_time"]) > 20 else spot.get("best_time", "N/A")),
        ("⏱️", "Time Needed", spot.get("estimated_time_needed", "N/A")[:20]),
    ]
    for i, (icon, label, value) in enumerate(badge_data):
        with col_badges[i]:
            st.markdown(f"<div class='info-badge'><div class='badge-icon'>{icon}</div><div class='badge-label'>{label}</div><div class='badge-value'>{value}</div></div>", unsafe_allow_html=True)

    # ── Image gallery ──
    if spot.get("images"):
        st.markdown("<h3>📸 Gallery</h3>", unsafe_allow_html=True)
        imgs = spot["images"]
        cols = st.columns(min(3, len(imgs)))
        for idx, img_data in enumerate(imgs[:3]):
            with cols[idx]:
                st.image(img_data.get("url", ""), caption=img_data.get("caption", ""), width="stretch")
        if len(imgs) > 3:
            with st.expander(f"📷 View all {len(imgs)} images"):
                remaining = st.columns(2)
                for idx, img_data in enumerate(imgs[3:]):
                    with remaining[idx % 2]:
                        st.image(img_data.get("url", ""), caption=img_data.get("caption", ""), width="stretch")

    # ── Detail tabs ──
    tab_labels = ["📖 Description", "🏛️ History", "💡 Tips & Avoid", "🚗 Getting There"]
    if spot.get("sections"):
        tab_labels.append("🗺️ Sections")
    if spot.get("visiting_guidance", {}).get("what_to_bring"):
        tab_labels.append("🎒 Packing List")
    if spot.get("nearby_attractions"):
        tab_labels.append("🗺️ Nearby")
    if spot.get("average_cost_per_person"):
        tab_labels.append("💰 Costs")

    tabs = st.tabs(tab_labels)
    tab_idx = 0

    with tabs[tab_idx]:  # Description
        tab_idx += 1
        desc = spot.get("description", "No description available.")
        st.markdown(f"<div style='line-height:1.7;font-size:1.05rem;'>{desc}</div>", unsafe_allow_html=True)
        # Activities list
        if spot.get("activities"):
            st.markdown("#### 🏞️ Activities")
            acts = spot["activities"]
            if isinstance(acts, str):
                for line in acts.strip().split("\n"):
                    line = line.strip().lstrip("- ")
                    if line:
                        st.markdown(f"- {line}")
            elif isinstance(acts, list):
                for a in acts:
                    st.markdown(f"- {a}")

    with tabs[tab_idx]:  # History
        tab_idx += 1
        hist = spot.get("history", "No historical information.")
        st.markdown(f"<div style='line-height:1.7;font-size:1.05rem;'>{hist}</div>", unsafe_allow_html=True)

    with tabs[tab_idx]:  # Tips
        tab_idx += 1
        col_tip1, col_tip2 = st.columns(2)
        with col_tip1:
            st.markdown("#### ✅ Pro Tips")
            tips = spot.get("tips", [])
            if isinstance(tips, str):
                for line in tips.strip().split("\n"):
                    line = line.strip().lstrip("- ")
                    if line:
                        st.markdown(f"- {line}")
            elif isinstance(tips, list):
                for tip in tips:
                    st.markdown(f"- {tip}")
            # Also check visiting_guidance tips
            vg_tips = spot.get("visiting_guidance", {}).get("tips", [])
            if vg_tips and isinstance(vg_tips, list):
                for tip in vg_tips:
                    st.markdown(f"- {tip}")
        with col_tip2:
            avoid = spot.get("visiting_guidance", {}).get("what_to_avoid", [])
            if avoid:
                st.markdown("#### ❌ What to Avoid")
                for a in avoid:
                    st.markdown(f"- ❌ {a}")
            # Best time detail
            if spot.get("best_time"):
                st.markdown("#### 🌿 When to Go")
                st.info(spot["best_time"])

    with tabs[tab_idx]:  # Getting There
        tab_idx += 1
        transport = spot.get("visiting_guidance", {}).get("getting_there", {})
        if transport and "options" in transport:
            for opt in transport["options"]:
                with st.expander(f"🚌 {opt['method']}", expanded=True):
                    st.markdown(f"<div style='line-height:1.6;'>{opt['details']}</div>", unsafe_allow_html=True)
        else:
            st.info("Transportation options available. Consider private car, tour bus, or public transit from Beijing.")

    # ── Sections ──
    if tab_idx < len(tab_labels) and tab_labels[tab_idx] == "🗺️ Sections":
        with tabs[tab_idx]:
            tab_idx += 1
            sections = spot.get("sections", {})
            if sections:
                section_names = list(sections.keys())
                # Comparison table first
                st.markdown("#### 📊 Section Comparison")
                comp_rows = []
                for sn in section_names:
                    s = sections[sn]
                    comp_rows.append({
                        "Section": sn,
                        "Difficulty": s.get("difficulty", "—"),
                        "Crowd": s.get("crowd_level", "—"),
                        "Best For": s.get("recommended_for", "—"),
                        "Travel Time": s.get("travel_time_from_beijing", "—"),
                    })
                st.dataframe(comp_rows, width="stretch", hide_index=True)

                st.markdown("#### 🔍 Explore Each Section")
                selected_section = st.selectbox("Choose a section", section_names, key=f"section_select_{spot.get('_slug', '')}")
                sec = sections[selected_section]

                diff_badge = _difficulty_badge(sec.get("difficulty", ""))
                st.markdown(f"<div style='display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.5rem;'><strong>Difficulty:</strong> {diff_badge}</div>", unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**👥 Crowd Level:** {sec.get('crowd_level', 'N/A')}")
                    st.markdown(f"**🎯 Best For:** {sec.get('recommended_for', 'N/A')}")
                    st.markdown(f"**⏱️ Travel Time:** {sec.get('travel_time_from_beijing', 'N/A')}")
                with c2:
                    st.markdown(f"**👍 Pros:** {sec.get('pros', 'N/A')}")
                    st.markdown(f"**👎 Cons:** {sec.get('cons', 'N/A')}")
                    if "nearby" in sec:
                        st.markdown(f"**📍 Nearby:** {sec['nearby']}")

                st.markdown(f"**Description:** {sec.get('description', 'N/A')}")
            else:
                st.write("Section details not available.")

    # ── Packing List ──
    if tab_idx < len(tab_labels) and tab_labels[tab_idx] == "🎒 Packing List":
        with tabs[tab_idx]:
            tab_idx += 1
            items = spot.get("visiting_guidance", {}).get("what_to_bring", [])
            st.markdown("#### 🎒 Recommended Packing List")
            cols_pack = st.columns(2)
            for i, item in enumerate(items):
                with cols_pack[i % 2]:
                    st.markdown(f"✅ {item}")

    # ── Nearby Attractions ──
    if tab_idx < len(tab_labels) and tab_labels[tab_idx] == "🗺️ Nearby":
        with tabs[tab_idx]:
            tab_idx += 1
            nearby = spot.get("nearby_attractions", [])
            for na in nearby:
                with st.container(border=True):
                    st.markdown(f"**{na.get('name', '')}** — *{na.get('distance', '')}*")
                    st.write(na.get("description", ""))

    # ── Cost Information ──
    if tab_idx < len(tab_labels) and tab_labels[tab_idx] == "💰 Costs":
        with tabs[tab_idx]:
            tab_idx += 1
            cost = spot.get("average_cost_per_person", "")
            st.markdown("#### 💰 Estimated Cost Per Person")
            st.markdown(f"<div style='line-height:1.6;'>{cost}</div>", unsafe_allow_html=True)

            # ── Interactive cost calculator ──
            st.markdown("#### 🧮 Quick Cost Calculator")
            calc_col1, calc_col2 = st.columns(2)
            with calc_col1:
                num_people = st.number_input("Number of people", min_value=1, max_value=20, value=2, key=f"ppl_{spot.get('_slug', '')}")
                budget_level = st.selectbox("Budget level", ["Budget", "Mid-range", "Luxury"], key=f"budget_{spot.get('_slug', '')}")
            with calc_col2:
                if "average_cost_per_person" in spot:
                    cost_text = spot["average_cost_per_person"].lower()
                    if "budget" in cost_text:
                        base_cost = 200
                    elif "luxury" in cost_text:
                        base_cost = 1200
                    else:
                        base_cost = 500
                else:
                    base_cost = 300

                multipliers = {"Budget": 0.8, "Mid-range": 1.0, "Luxury": 1.8}
                est_total = int(base_cost * num_people * multipliers[budget_level])
                st.metric("Estimated Total", f"¥{est_total:,}", help="Rough estimate for transport + entrance + meals")
                st.caption("Prices vary by season and exchange rate.")

    # ── Navigation buttons ──
    st.markdown("---")
    if not full_page:
        col_back, col_full = st.columns(2)
        with col_back:
            if st.button("🔙 Back to Attractions", width="stretch", type="primary"):
                st.session_state["beijing_view"] = "list"
                st.session_state["selected_spot_slug"] = None
                st.session_state["full_mode_spot"] = None
                st.rerun()
        with col_full:
            if st.button("📺 View Full Page", width="stretch"):
                st.session_state["full_mode_spot"] = spot
                st.rerun()
    else:
        if st.button("✖️ Exit Full Page", width="stretch", type="primary"):
            st.session_state["full_mode_spot"] = None
            st.session_state["beijing_view"] = "list"
            st.rerun()
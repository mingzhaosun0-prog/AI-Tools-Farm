import streamlit as st
import yaml
import os
import glob
import json
from datetime import datetime
from services.i18n import t, get_language

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

def _parse_hours(time_str: str) -> float:
    """Parse '3-4 hours' or '2h' or '30 min' into float hours."""
    if not time_str or time_str == "—":
        return 2.0
    t = time_str.lower().strip()
    # "3-4 hours" → take min
    import re
    nums = re.findall(r"(\d+\.?\d*)", t)
    if not nums:
        return 2.0
    if "+" in t:
        return float(nums[0]) + 1.0
    return float(nums[0])


def _parse_cost(price_str: str) -> int:
    """Extract a numeric cost (lowest value) from a ticket price string."""
    if not price_str or price_str == "—":
        return 0
    import re
    nums = re.findall(r"¥(\d+[\d,]*)", price_str)
    if not nums:
        nums = re.findall(r"(\d+[\d,]*)", price_str)
    if not nums:
        return 0
    try:
        return int(nums[0].replace(",", ""))
    except ValueError:
        return 0


def _weather_tip():
    """Return simple seasonal advice."""
    month = datetime.now().month
    if 3 <= month <= 5:
        return "🌸", t("spring"), t("spring_desc")
    elif 6 <= month <= 8:
        return "☀️", t("summer"), t("summer_desc")
    elif 9 <= month <= 11:
        return "🍂", t("autumn"), t("autumn_desc")
    else:
        return "❄️", t("winter"), t("winter_desc")


def _localized_text(spot: dict, field: str, lang: str = None) -> str:
    """Get field text in current language, falling back to English/default."""
    if lang is None:
        lang = get_language()
    # Check for language-specific field (e.g. 'description_zh')
    localized = spot.get(f"{field}_{lang}")
    if localized:
        return localized
    # Fallback to default field
    return spot.get(field, "")


# ── SEO / Structured Data ────────────────────────────────

def _inject_seo_tags(title: str, description: str, city: str = "Beijing"):
    """Inject JSON-LD structured data for rich Google search results."""
    import uuid
    page_id = f"https://ai-tools-farm.streamlit.app/#{uuid.uuid4().hex[:8]}"
    structured = {
        "@context": "https://schema.org",
        "@type": "TouristAttraction",
        "@id": page_id,
        "name": title,
        "description": description[:200],
        "touristType": "International Visitors",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": city,
            "addressCountry": "CN"
        },
        "potentialAction": {
            "@type": "SearchAction",
            "target": "https://ai-tools-farm.streamlit.app/?search={search_term}",
            "query-input": "required name=search_term"
        }
    }
    st.markdown(f"""
    <meta name="description" content="{description[:160]}">
    <meta name="keywords" content="China travel, {city}, Beijing attractions, Great Wall, Forbidden City, travel guide China, {city} tour, China tourism">
    <meta name="geo.region" content="CN-{city[:2].upper()}">
    <meta name="geo.placename" content="{city.title()}">
    <meta name="ICBM" content="39.9042, 116.4074">
    <link rel="alternate" hreflang="en" href="https://ai-tools-farm.streamlit.app/">
    <link rel="alternate" hreflang="zh" href="https://ai-tools-farm.streamlit.app/?lang=zh">
    <link rel="alternate" hreflang="x-default" href="https://ai-tools-farm.streamlit.app/">
    <script type="application/ld+json" id="seo-{uuid.uuid4().hex[:8]}">
    {json.dumps(structured, indent=2, ensure_ascii=False)}
    </script>
    """, unsafe_allow_html=True)

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
    city_display = t(f'city_{city}', city.title())
    city = st.selectbox(f"📍 {t('choose_city')}", cities, index=0 if "beijing" in cities else 0,
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
    _inject_seo_tags(
        f"China Travel Guide — {city_display} Attractions",
        f"Explore top attractions in {city_display}, China. Interactive guides with cost calculators, section comparisons, seasonal tips & planning tools.",
        city.title()
    )
    hero_bg = "linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #e74c3c 100%)"
    st.markdown(
        f"<div style='background:{hero_bg};padding:2.5rem 2rem;border-radius:1.5rem;"
        f"margin-bottom:2rem;text-align:center;color:white;box-shadow:0 8px 32px rgba(0,0,0,0.15);'>"
        f"<h1 style='margin:0;font-size:2.8rem;'>&#127944; {t('app_title')}</h1>"
        f"<p style='margin:0.5rem 0 0 0;font-size:1.2rem;opacity:0.9;'>"
        f"{t('hero_subtitle').replace('{cities', '').replace('}', '')}</p>"
        f"<div style='margin-top:1rem;display:inline-block;background:rgba(255,255,255,0.15);"
        f"padding:0.5rem 1.5rem;border-radius:2rem;'>{season_icon} "
        f"<strong>{season_name}</strong> &mdash; {season_desc}</div></div>",
        unsafe_allow_html=True
    )

    if not attractions:
        st.info(t('no_attractions', '✨ No attractions loaded yet for **{city}**. Add YAML files to `travel/data/{city}/`.').replace('{city}', city_display))
        return

    # ── Stats banner ──
    total_spots = len(attractions)
    top_rated = max(a.get("rating", 0) for a in attractions.values())
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.markdown(f"<div class='stat-card'><div class='stat-num'>{total_spots}</div><div class='stat-label'>{t('attractions')}</div></div>", unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"<div class='stat-card'><div class='stat-num'>{top_rated}★</div><div class='stat-label'>{t('top_rated', 'Top Rated')}</div></div>", unsafe_allow_html=True)
    with col_s3:
        cities_total = len([d for d in os.listdir(TRAVEL_DATA_DIR) if os.path.isdir(os.path.join(TRAVEL_DATA_DIR, d)) and not d.startswith("_")])
        st.markdown(f"<div class='stat-card'><div class='stat-num'>{cities_total}</div><div class='stat-label'>{t('cities')}</div></div>", unsafe_allow_html=True)
    with col_s4:
        sections_count = sum(len(a.get("sections", {})) for a in attractions.values())
        st.markdown(f"<div class='stat-card'><div class='stat-num'>{sections_count}</div><div class='stat-label'>{t('sections_count','Sections')}</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    # ── Attraction cards ──
    st.markdown(f"<h2>🏛️ {t('top_attractions').replace('{city}', city_display)}</h2>", unsafe_allow_html=True)

    # Sort by rating descending
    sorted_attractions = sorted(attractions.values(), key=lambda x: x.get("rating", 0), reverse=True)

    for spot in sorted_attractions:
        _render_attraction_card(spot)

    # ═══════════════════════════════════════════════════
    # TOP 3: PLAN MY DAY — Full trip planner
    # ═══════════════════════════════════════════════════
    with st.expander("🗓️ Plan My Day — Build Your Perfect Day Trip", expanded=False):
        st.markdown("Pick attractions and get an optimised route with time estimates & costs.")
        spot_names = {a["name"]: a for a in attractions.values()}
        all_names = list(spot_names.keys())

        selected_plan = st.multiselect(
            "Select attractions for your day trip",
            all_names,
            default=all_names[:min(3, len(all_names))],
            max_selections=5,
            key="plan_my_day_sel"
        )

        if len(selected_plan) >= 1:
            col_plan_left, col_plan_right = st.columns([3, 2])

            with col_plan_left:
                st.markdown("#### 🗺️ Suggested Route Order")
                # Sorted by estimated time needed (shorter first = morning, longer = afternoon)
                sorted_plan = sorted(
                    selected_plan,
                    key=lambda n: _parse_hours(spot_names[n].get("estimated_time_needed", "2h"))
                )

                total_time = 0
                total_cost = 0
                route_lines = []
                for idx, name in enumerate(sorted_plan):
                    s = spot_names[name]
                    hrs = _parse_hours(s.get("estimated_time_needed", "2h"))
                    total_time += hrs + 0.5  # +30 min travel between spots

                    # Extract base cost
                    ticket_str = s.get("ticket_price", "¥0")
                    cost = _parse_cost(ticket_str)
                    total_cost += cost

                    travel_note = ""
                    if idx > 0:
                        travel_note = " 🚶 → *(30 min travel)*"
                    time_str = s.get("estimated_time_needed", "—")
                    route_lines.append(
                        f"**{idx+1}. {name}** ⏱️ {time_str}{travel_note}"
                    )

                for line in route_lines:
                    st.markdown(f"- {line}")

                st.markdown("---")
                st.success(f"**Total estimated time: {total_time:.1f} hours** — Start at 08:00 → Finish ~{8+total_time:.0f}:00")

            with col_plan_right:
                st.markdown("#### 💰 Cost Breakdown")
                for name in sorted_plan:
                    s = spot_names[name]
                    ticket_str = s.get("ticket_price", "¥0")
                    cost = _parse_cost(ticket_str)
                    short_ticket = (ticket_str[:28] + "…") if len(ticket_str) > 28 else ticket_str
                    st.markdown(f"- **{name}** → {short_ticket}")

                st.markdown(f"---")
                st.info(f"**🎟️ Total entry: ~¥{total_cost:,}** per person")

            # Export plan
            if st.button("📋 Copy This Plan to Clipboard", key="copy_plan", use_container_width=True):
                plan_text = f"🗓️ My Day Trip Plan ({len(selected_plan)} attractions)\n"
                plan_text += "=" * 40 + "\n"
                for idx, name in enumerate(sorted_plan):
                    plan_text += f"{idx+1}. {name}\n"
                plan_text += f"\nTotal time: ~{total_time:.1f} hours\n"
                plan_text += f"Total cost: ~¥{total_cost:,} per person\n"
                st.code(plan_text, language="text")
                st.toast("✅ Plan ready! Copy the code block above.", icon="📋")
        else:
            st.info("Select at least one attraction to start planning.")

    # ═══════════════════════════════════════════════════
    # Quick Planning Tools
    # ═══════════════════════════════════════════════════
    with st.expander("🧭 Travel Planning Tools", expanded=False):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("#### 📅 Best Times to Visit")
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

    # ═══════════════════════════════════════════════════
    # Compare attractions
    # ═══════════════════════════════════════════════════
    with st.expander("⚖️ Compare Attractions Side-by-Side", expanded=False):
        names = [a["name"] for a in attractions.values()]
        selected = st.multiselect("Select 2-4 attractions to compare", names, default=names[:min(2, len(names))])
        if len(selected) >= 2:
            comp_data = []
            for a in attractions.values():
                if a["name"] in selected:
                    # Determine difficulty
                    secs = a.get("sections", {})
                    diff = "—"
                    if secs:
                        diffs = [s.get("difficulty", "") for s in secs.values()]
                        diff = diffs[0] if diffs else "—"
                    comp_data.append({
                        "Attraction": a["name"],
                        "Rating ★": a.get("rating", "—"),
                        "Difficulty": diff,
                        "Ticket (¥)": (a.get("ticket_price", "")[:28] + "…") if a.get("ticket_price") and len(a["ticket_price"]) > 28 else a.get("ticket_price", "—"),
                        "Hours": (a.get("opening_hours", "")[:30] + "…") if a.get("opening_hours") and len(a["opening_hours"]) > 30 else a.get("opening_hours", "—"),
                        "Time Needed": a.get("estimated_time_needed", "—"),
                        "Sections": len(secs),
                    })
            st.dataframe(comp_data, width="stretch", hide_index=True)
        else:
            st.info("Select at least 2 attractions to compare.")


def _crowd_badge(crowd_text: str) -> str:
    """Return an emoji-based crowd indicator from a crowd_level string."""
    t = crowd_text.lower()
    if any(w in t for w in ["very crowded", "extremely crowded", "crowded"]):
        return "🔴 Very Crowded"
    elif any(w in t for w in ["moderately", "moderate"]):
        return "🟡 Moderate"
    elif any(w in t for w in ["sparse", "quiet", "peaceful"]):
        return "🟢 Quiet"
    return "⚪ Unknown"


def _render_attraction_card(spot: dict):
    """Render a single attraction card with rich visuals — image, badges, quick info."""
    rating_html = _star_rating(spot.get("rating", 0))
    sections_count = len(spot.get("sections", {}))

    # ── Difficulty badge ──
    difficulty = "—"
    sections = spot.get("sections", {})
    if sections:
        # Use the easiest section as overall difficulty indicator
        diffs = [s.get("difficulty", "").lower() for s in sections.values()]
        if any(d == "easy" for d in diffs):
            difficulty = "Easy"
        elif any(d in ("moderate",) for d in diffs):
            difficulty = "Moderate"
        elif any(d in ("challenging",) for d in diffs):
            difficulty = "Challenging"
        elif any(d in ("strenuous",) for d in diffs):
            difficulty = "Strenuous"
    diff_badge = _difficulty_badge(difficulty)

    # ── Crowd indicator ──
    crowd_html = ""
    highest_crowd = "moderate"
    for s in sections.values():
        cl = s.get("crowd_level", "").lower()
        if "very crowded" in cl or "extremely crowded" in cl:
            highest_crowd = "very crowded"
        elif "moderate" in cl and highest_crowd != "very crowded":
            highest_crowd = "moderate"
        elif "sparse" in cl or "quiet" in cl and highest_crowd not in ("very crowded", "moderate"):
            highest_crowd = "sparse"
    crowd_display = {"very crowded": "🔴 Crowded", "moderate": "🟡 Moderate", "sparse": "🟢 Quiet"}
    crowd_html = f"<span class='tag'>{crowd_display.get(highest_crowd, '⚪ —')}</span>"

    # ── Image thumbnail ──
    thumb_html = ""
    if spot.get("images"):
        img_url = spot["images"][0]["url"]
        thumb_html = f"<img src='{img_url}' style='width:100%;height:160px;object-fit:cover;border-radius:1rem 1rem 0 0;margin-bottom:0.5rem;' alt='{spot['name']}'>"

    # ── Build tag items ──
    tags = []
    hours = spot.get("opening_hours", "N/A")
    if len(hours) > 30:
        hours = hours[:30] + "…"
    tags.append(f"<span class='tag'>🕒 {hours}</span>")

    if sections_count:
        label = "section" if sections_count == 1 else "sections"
        tags.append(f"<span class='tag'>🗺️ {sections_count} {label}</span>")

    acts = spot.get("activities", "")
    if len(acts) > 28:
        acts = acts[:28] + "…"
    if acts:
        tags.append(f"<span class='tag'>🏞️ {acts}</span>")

    # Truncate ticket price
    ticket = spot.get("ticket_price", "N/A")
    if len(ticket) > 40:
        ticket = ticket[:40] + "…"

    # Time needed
    time_needed = spot.get("estimated_time_needed", "—")

    # Time bar
    time_bar = ""
    if time_needed != "—":
        try:
            hours_val = int(time_needed.split("-")[0].split("h")[0].strip())
            filled = min(hours_val, 8)
            empty = 8 - filled
            time_bar = "█" * filled + "░" * empty
            time_bar = f"<span style='font-size:0.75rem;font-family:monospace;color:#475569;'>{time_bar} {time_needed}</span>"
        except (ValueError, IndexError):
            time_bar = f"<span style='font-size:0.8rem;color:#475569;'>⏱️ {time_needed}</span>"

    # Build card HTML — use inline styles to avoid markdown interference
    tags_html = " ".join(tags)
    card_html = (
        "<div style='background:white;border-radius:1.2rem;overflow:hidden;"
        "margin:1rem 0;box-shadow:0 2px 12px rgba(0,0,0,0.05);border:1px solid #e9ecef;'>"
        f"{thumb_html}"
        "<div style='padding:1.5rem;'>"
        "<div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;'>"
        f"<h3 style='margin:0;font-size:1.4rem;color:#1e293b;'>{spot['name']} "
        f"<span style='color:#e74c3c;font-size:0.85em;'>&#25915;&#30053;</span></h3>"
        f"<div>{rating_html}</div>"
        "</div>"
        f"<div style='color:#64748b;margin:0.3rem 0 0.8rem;font-size:0.95rem;'>{_localized_text(spot,'subtitle')}</div>"
        "<div style='display:flex;flex-wrap:wrap;gap:1rem;margin-bottom:0.6rem;font-size:0.9rem;color:#475569;'>"
        f"<span>&#128205; {spot.get('location', 'N/A')}</span>"
        f"<span>&#127934; {ticket}</span>"
        f"<span>{time_bar}</span>"
        "</div>"
        "<div style='display:flex;flex-wrap:wrap;gap:0.5rem;'>"
        f"{diff_badge} {crowd_html} {tags_html}"
        "</div></div></div>"
    )

    st.markdown(card_html, unsafe_allow_html=True)

    col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
    with col_b1:
        if st.button(f"🔍 View Details — {spot['name']}", key=f"view_{spot['_slug']}", use_container_width=True):
            st.session_state["beijing_view"] = "detail"
            st.session_state["selected_spot_slug"] = spot["_slug"]
            st.session_state["full_mode_spot"] = None
            st.rerun()
    with col_b2:
        if st.button(f"🗺️ Full Page", key=f"full_{spot['_slug']}", use_container_width=True):
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
            use_container_width=True
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

    # ── SEO structured data for this attraction ──
    _inject_seo_tags(
        f"{spot['name']} — Beijing China",
        spot.get("description", f"Visit {spot['name']} in Beijing. {spot.get('history', '')}"),
        "Beijing"
    )

    # ── Hero header ──
    bg_style = ""
    if spot.get("images"):
        bg_style = f"background:linear-gradient(rgba(0,0,0,0.55),rgba(0,0,0,0.55)),url('{spot['images'][0]['url']}') center/cover;"
    else:
        bg_style = "background:linear-gradient(135deg,#1e3c72,#2a5298);"
    fs = '"2.8rem"' if full_page else '"2.2rem"'
    ss = '"1.3rem"' if full_page else '"1.1rem"'

    st.markdown(
        f"<div style='{bg_style}padding:3rem 2rem 2rem;border-radius:1.5rem;"
        f"margin-bottom:1.5rem;text-align:center;color:white;min-height:220px;"
        f"display:flex;flex-direction:column;justify-content:center;'>"
        f"<h1 style='margin:0;font-size:{fs};'>{spot['name']}"
        f" <span style='color:#ffd700;font-size:0.75em;margin-left:0.5rem;'>{t('guide_word','攻略')}</span></h1>"
        f"<p style='margin:0.3rem 0 0.5rem;font-size:{ss};opacity:0.9;'>{_localized_text(spot,'subtitle')}</p>"
        f"<div>{rating_html}</div></div>",
        unsafe_allow_html=True
    )

    # ── Quick info badges ──
    col_badges = st.columns(5)
    badge_data = [
        ("📍", t('location','Location'), spot.get("location", "N/A")[:25]),
        ("🕒", t('hours','Hours'), (spot.get("opening_hours", "")[:20] + "…") if spot.get("opening_hours") and len(spot["opening_hours"]) > 20 else spot.get("opening_hours", "N/A")),
        ("🎟️", t('ticket','Ticket'), (spot.get("ticket_price", "")[:20] + "…") if spot.get("ticket_price") and len(spot["ticket_price"]) > 20 else spot.get("ticket_price", "N/A")),
        ("🌿", t('best_time','Best Time'), (spot.get("best_time", "")[:20] + "…") if spot.get("best_time") and len(spot["best_time"]) > 20 else spot.get("best_time", "N/A")),
        ("⏱️", t('time_needed','Time Needed'), spot.get("estimated_time_needed", "N/A")[:20]),
    ]
    for i, (icon, label, value) in enumerate(badge_data):
        with col_badges[i]:
            st.markdown(f"<div class='info-badge'><div class='badge-icon'>{icon}</div><div class='badge-label'>{label}</div><div class='badge-value'>{value}</div></div>", unsafe_allow_html=True)

    # ── Image gallery ──
    if spot.get("images"):
        st.markdown(f"<h3>&#128248; {t('photo_gallery','Gallery')}</h3>", unsafe_allow_html=True)
        imgs = spot["images"]
        cols = st.columns(min(3, len(imgs)))
        for idx, img_data in enumerate(imgs[:3]):
            with cols[idx]:
                st.image(img_data.get("url", ""), caption=img_data.get("caption", ""), width="stretch")
        if len(imgs) > 3:
            with st.expander(f"&#128247; {t('view_all_images','View all {n} images').replace('{n}', str(len(imgs)))}"):
                remaining = st.columns(2)
                for idx, img_data in enumerate(imgs[3:]):
                    with remaining[idx % 2]:
                        st.image(img_data.get("url", ""), caption=img_data.get("caption", ""), width="stretch")

    # ── Detail tabs ──
    tab_labels = [f"📖 {t('description')}", f"🏛️ {t('history')}", f"💡 {t('tips')}", f"🚗 {t('getting_there')}"]
    if spot.get("sections"):
        tab_labels.append(f"🗺️ {t('sections_count','Sections')}")
    if spot.get("visiting_guidance", {}).get("what_to_bring"):
        tab_labels.append(f"🎒 {t('packing_list')}")
    if spot.get("nearby_attractions"):
        tab_labels.append(f"🗺️ {t('nearby')}")
    if spot.get("average_cost_per_person"):
        tab_labels.append(f"💰 {t('costs')}")

    tabs = st.tabs(tab_labels)
    tab_idx = 0

    with tabs[tab_idx]:  # Description
        tab_idx += 1
        desc = _localized_text(spot, "description") or "No description available."
        st.markdown(f"<div style='line-height:1.7;font-size:1.05rem;'>{desc}</div>", unsafe_allow_html=True)
        # Activities list
        if spot.get("activities"):
            st.markdown(f"#### &#127965;&#65039; {t('activities','Activities')}")
            acts = _localized_text(spot, "activities")
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
        hist = _localized_text(spot, "history") or "No historical information."
        st.markdown(f"<div style='line-height:1.7;font-size:1.05rem;'>{hist}</div>", unsafe_allow_html=True)

    with tabs[tab_idx]:  # Tips
        tab_idx += 1
        col_tip1, col_tip2 = st.columns(2)
        with col_tip1:
            st.markdown(f"#### &#10004;&#65039; {t('pro_tips','Pro Tips')}")
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
                st.markdown(f"#### &#10060; {t('what_to_avoid','What to Avoid')}")
                for a in avoid:
                    st.markdown(f"- ❌ {a}")
            # Best time detail
            if spot.get("best_time"):
                st.markdown(f"#### &#127800; {t('when_to_go','When to Go')}")
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
                st.markdown(f"#### &#128202; {t('section_comparison')}")
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

                st.markdown(f"#### &#128269; {t('explore_section')}")
                selected_section = st.selectbox(t('choose_section'), section_names, key=f"section_select_{spot.get('_slug', '')}")
                sec = sections[selected_section]

                diff_badge = _difficulty_badge(sec.get("difficulty", ""))
                st.markdown(f"<div style='display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.5rem;'><strong>Difficulty:</strong> {diff_badge}</div>", unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**&#128100; {t('crowd_level')}:** {sec.get('crowd_level', 'N/A')}")
                    st.markdown(f"**&#127919; {t('best_for')}:** {sec.get('recommended_for', 'N/A')}")
                    st.markdown(f"**&#9201;&#65039; {t('travel_time')}:** {sec.get('travel_time_from_beijing', 'N/A')}")
                with c2:
                    st.markdown(f"**&#128077; {t('pros')}:** {sec.get('pros', 'N/A')}")
                    st.markdown(f"**&#128078; {t('cons')}:** {sec.get('cons', 'N/A')}")
                    if "nearby" in sec:
                        st.markdown(f"**&#128205; Nearby:** {sec['nearby']}")

                st.markdown(f"**Description:** {sec.get('description', 'N/A')}")
            else:
                st.write("Section details not available.")

    # ── Packing List ──
    if tab_idx < len(tab_labels) and tab_labels[tab_idx] == "🎒 Packing List":
        with tabs[tab_idx]:
            tab_idx += 1
            items = spot.get("visiting_guidance", {}).get("what_to_bring", [])
            st.markdown(f"#### &#127873; {t('recommended_packing')}")
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
            st.markdown(f"#### &#128176; {t('estimated_cost','Estimated Cost Per Person')}")
            st.markdown(f"<div style='line-height:1.6;'>{cost}</div>", unsafe_allow_html=True)

            # ── Interactive cost calculator ──
            st.markdown(f"#### &#129518; {t('quick_cost_calc')}")
            calc_col1, calc_col2 = st.columns(2)
            with calc_col1:
                num_people = st.number_input(t('people','Number of people'), min_value=1, max_value=20, value=2, key=f"ppl_{spot.get('_slug', '')}")
                budget_level = st.selectbox(t('budget_level','Budget level'), ["Budget", "Mid-range", "Luxury"], key=f"budget_{spot.get('_slug', '')}")
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
                st.metric(t('estimated_total','Estimated Total'), f"¥{est_total:,}", help="Rough estimate for transport + entrance + meals")
                st.caption(t('prices_vary','Prices vary by season and exchange rate.'))

    # ── Navigation buttons ──
    st.markdown("---")
    if not full_page:
        col_back, col_full = st.columns(2)
        with col_back:
            if st.button(f"🔙 {t('back_to_attractions')}", use_container_width=True, type="primary"):
                st.session_state["beijing_view"] = "list"
                st.session_state["selected_spot_slug"] = None
                st.session_state["full_mode_spot"] = None
                st.rerun()
        with col_full:
            if st.button(f"📺 {t('full_page')}", use_container_width=True):
                st.session_state["full_mode_spot"] = spot
                st.rerun()
    else:
        if st.button(f"✖️ {t('exit_full_page')}", use_container_width=True, type="primary"):
            st.session_state["full_mode_spot"] = None
            st.session_state["beijing_view"] = "list"
            st.rerun()
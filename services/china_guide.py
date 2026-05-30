def show_spot_detail(spot, full_page=False):
    """
    Display detailed information for a single spot.
    If full_page=True, use a minimal layout (no side columns).
    """
    if not full_page:
        st.markdown(f"<h1 style='text-align: center;'>{spot['name']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: #555;'>{spot.get('subtitle', '')}</h3>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h1 style='text-align: center; font-size: 3rem;'>{spot['name']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: #555; font-size: 1.6rem;'>{spot.get('subtitle', '')}</h3>", unsafe_allow_html=True)
        st.markdown("---")
    
    # Display images if available
    if 'images' in spot and spot['images']:
        st.markdown("### 📸 Gallery")
        cols = st.columns(min(3, len(spot['images'])))
        for idx, img_data in enumerate(spot['images'][:3]):  # Show up to 3 images
            with cols[idx]:
                st.image(img_data.get('url', ''), caption=img_data.get('caption', ''), use_container_width=True)
        if len(spot['images']) > 3:
            with st.expander("View more images"):
                for img_data in spot['images'][3:]:
                    st.image(img_data.get('url', ''), caption=img_data.get('caption', ''), use_container_width=True)
    
    # Two columns for quick facts
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📍 Location**")
        st.write(spot.get('location', 'N/A'))
        st.markdown("**🕒 Opening Hours**")
        st.write(spot.get('opening_hours', 'N/A'))
        st.markdown("**🎟️ Ticket Price**")
        st.write(spot.get('ticket_price', 'N/A'))
    with col2:
        st.markdown("**🌿 Best Time to Visit**")
        st.write(spot.get('best_time', 'N/A'))
        st.markdown("**🏞️ Activities**")
        st.write(spot.get('activities', 'N/A'))
        st.markdown("**⏱️ Time Needed**")
        st.write(spot.get('estimated_time_needed', 'N/A'))
    
    # Description and history using tabs (more tabs for additional sections)
    tabs = ["📖 Description", "🏛️ History", "💡 Tips", "🚗 Getting There", "🗺️ Sections"]
    if 'visiting_guidance' in spot:
        tabs.insert(4, "🎒 What to Bring")
    
    tab_objects = st.tabs(tabs)
    
    with tab_objects[0]:  # Description
        st.write(spot.get('description', 'No description available.'))
    
    with tab_objects[1]:  # History
        st.write(spot.get('history', 'No historical information.'))
    
    with tab_objects[2]:  # Tips
        tips = spot.get('tips', [])
        if isinstance(tips, list):
            for tip in tips:
                st.markdown(f"- {tip}")
        else:
            st.write(tips)
        
        # Additional avoidance tips
        if 'visiting_guidance' in spot and 'what_to_avoid' in spot['visiting_guidance']:
            st.markdown("### ❌ What to Avoid")
            for avoid in spot['visiting_guidance']['what_to_avoid']:
                st.markdown(f"- {avoid}")
    
    with tab_objects[3]:  # Getting There
        if 'visiting_guidance' in spot and 'getting_there' in spot['visiting_guidance']:
            transport = spot['visiting_guidance']['getting_there']
            if 'options' in transport:
                for opt in transport['options']:
                    with st.expander(f"🚌 {opt['method']}"):
                        st.write(opt['details'])
        else:
            st.write("Transportation options available. Consider private car, tour bus, or public transit from Beijing.")
    
    if len(tab_objects) > 4 and tab_objects[4].label == "🗺️ Sections":
        with tab_objects[4]:  # Sections
            if 'sections' in spot:
                section_names = list(spot['sections'].keys())
                selected_section = st.selectbox("Choose a section for details", section_names)
                section = spot['sections'][selected_section]
                cols_section = st.columns(2)
                with cols_section[0]:
                    st.markdown(f"**Difficulty:** {section.get('difficulty', 'N/A')}")
                    st.markdown(f"**Crowd Level:** {section.get('crowd_level', 'N/A')}")
                    st.markdown(f"**Travel Time:** {section.get('travel_time_from_beijing', 'N/A')}")
                with cols_section[1]:
                    st.markdown(f"**Best For:** {section.get('recommended_for', 'N/A')}")
                st.markdown(f"**Description:** {section.get('description', 'N/A')}")
                st.markdown(f"**👍 Pros:** {section.get('pros', 'N/A')}")
                st.markdown(f"**👎 Cons:** {section.get('cons', 'N/A')}")
                if 'nearby' in section:
                    st.markdown(f"**Nearby:** {section['nearby']}")
            else:
                st.write("Section details not available for this attraction.")
    
    # Additional tab for "What to Bring" if exists
    if 'visiting_guidance' in spot and 'what_to_bring' in spot['visiting_guidance']:
        # Find the index of the "What to Bring" tab (we inserted it at position 4 if it exists)
        for idx, tab in enumerate(tab_objects):
            if tab.label == "🎒 What to Bring":
                with tab_objects[idx]:
                    st.markdown("### Recommended Packing List")
                    for item in spot['visiting_guidance']['what_to_bring']:
                        st.markdown(f"- {item}")
                break
    
    # Nearby attractions expander
    if 'nearby_attractions' in spot:
        with st.expander("🗺️ Nearby Attractions"):
            for attraction in spot['nearby_attractions']:
                st.markdown(f"**{attraction.get('name', 'N/A')}** ({attraction.get('distance', 'N/A')})")
                st.write(attraction.get('description', ''))
    
    # Cost information
    if 'average_cost_per_person' in spot:
        with st.expander("💰 Estimated Costs (per person)"):
            st.write(spot['average_cost_per_person'])
    
    # Action buttons
    if not full_page:
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔙 Back to Beijing Attractions", use_container_width=True):
                st.session_state["beijing_view"] = "list"
                st.session_state["full_mode_spot"] = None
                st.rerun()
        with col_btn2:
            if st.button("🔍 View Full Page", use_container_width=True):
                st.session_state["full_mode_spot"] = spot
                st.rerun()
    else:
        if st.button("✖️ Exit Full Page", use_container_width=True):
            st.session_state["full_mode_spot"] = None
            st.rerun()
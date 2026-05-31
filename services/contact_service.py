"""
Contact/Email service for the China Travel Guide.
Stores inquiries locally, exposed via a contact form.
"""

import streamlit as st
import json
import os
from datetime import datetime


INQUIRIES_PATH = "data/inquiries.json"


def _load_inquiries():
    """Load saved inquiries."""
    if os.path.exists(INQUIRIES_PATH):
        with open(INQUIRIES_PATH, "r") as f:
            return json.load(f)
    return []


def _save_inquiry(data: dict):
    """Save an inquiry."""
    inquiries = _load_inquiries()
    inquiries.append(data)
    os.makedirs(os.path.dirname(INQUIRIES_PATH), exist_ok=True)
    with open(INQUIRIES_PATH, "w") as f:
        json.dump(inquiries, f, indent=2, ensure_ascii=False)


def display_contact_form():
    """Display a contact form that saves inquiries locally."""
    st.markdown("""
    <h3 style="text-align:center;">📧 Contact Us</h3>
    <p style="text-align:center;color:#64748b;">
        Have a question about a destination, need travel advice, or want to partner with us? 
        Drop us a message and we'll get back to you.
    </p>
    """, unsafe_allow_html=True)

    with st.form("contact_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Your Name", placeholder="e.g. John Smith")
        with col2:
            email = st.text_input("Your Email", placeholder="e.g. john@example.com")

        subject = st.text_input("Subject", placeholder="e.g. Question about Great Wall tickets")

        message = st.text_area("Message", placeholder="Tell us how we can help...", height=150)

        col_submit, _ = st.columns([1, 2])
        with col_submit:
            submitted = st.form_submit_button("📨 Send Message", use_container_width=True, type="primary")

        if submitted:
            if not name or not email or not message:
                st.error("Please fill in your name, email, and message.")
            else:
                inquiry = {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                    "name": name,
                    "email": email,
                    "subject": subject or "(No subject)",
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "status": "unread"
                }
                _save_inquiry(inquiry)
                st.success(f"✅ Thanks {name}! Your message has been received. We'll respond within 24 hours.")
                st.balloons()


def display_inquiry_dashboard():
    """Admin dashboard to view inquiries (premium/owner only)."""
    inquiries = _load_inquiries()
    unread = [i for i in inquiries if i.get("status") == "unread"]

    st.markdown(f"### 📋 Inquiries Dashboard ({len(unread)} unread / {len(inquiries)} total)")

    if not inquiries:
        st.info("No inquiries yet.")
        return

    for idx, inq in enumerate(reversed(inquiries)):
        status_icon = "🆕" if inq.get("status") == "unread" else "✅"
        with st.expander(f"{status_icon} {inq.get('subject','(No subject)')} — {inq.get('name','?')} ({inq.get('timestamp','?')[:10]})"):
            st.markdown(f"**From:** {inq.get('name')} ({inq.get('email')})")
            st.markdown(f"**Date:** {inq.get('timestamp')}")
            st.markdown(f"**Subject:** {inq.get('subject')}")
            st.markdown(f"**Message:**")
            st.markdown(f"<div style='background:#f8fafc;padding:1rem;border-radius:0.5rem;line-height:1.6;'>{inq.get('message')}</div>", unsafe_allow_html=True)

            if inq.get("status") == "unread":
                if st.button("✅ Mark as Read", key=f"mark_read_{idx}"):
                    inquiries[-1 - idx]["status"] = "read"
                    os.makedirs(os.path.dirname(INQUIRIES_PATH), exist_ok=True)
                    with open(INQUIRIES_PATH, "w") as f:
                        json.dump(inquiries, f, indent=2, ensure_ascii=False)
                    st.rerun()

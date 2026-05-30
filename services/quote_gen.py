# services/quote_gen.py
import streamlit as st
import random

def quote_generator():
    """App 4: Random Quote Generator - motivational/inspirational."""
    st.markdown("<h2 style='text-align: center;'>💬 Random Quote Generator</h2>", unsafe_allow_html=True)
    
    quotes = [
        ("The only limit to our realization of tomorrow is our doubts of today.", "Franklin D. Roosevelt"),
        ("Do not wait to strike till the iron is hot; but make it hot by striking.", "William Butler Yeats"),
        ("It always seems impossible until it's done.", "Nelson Mandela"),
        ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
        ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill"),
        ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
        ("Act as if what you do makes a difference. It does.", "William James"),
        ("Keep your face always toward the sunshine—and shadows will fall behind you.", "Walt Whitman"),
        ("What you get by achieving your goals is not as important as what you become by achieving your goals.", "Zig Ziglar"),
        ("Start where you are. Use what you have. Do what you can.", "Arthur Ashe"),
    ]
    
    if st.button("✨ Generate New Quote", use_container_width=True):
        st.session_state["quote_idx"] = random.randint(0, len(quotes)-1)
    
    if "quote_idx" not in st.session_state:
        st.session_state["quote_idx"] = random.randint(0, len(quotes)-1)
    
    quote_text, author = quotes[st.session_state["quote_idx"]]
    
    st.markdown(f"""
    <div style="background-color: #fef9e3; padding: 2rem; border-radius: 2rem; text-align: center; margin: 1rem 0; border-left: 6px solid #f59e0b;">
        <p style="font-size: 1.8rem; font-style: italic; color: #2d3748;">“{quote_text}”</p>
        <p style="font-size: 1.2rem; color: #b45309;">— {author}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.code(f"“{quote_text}” — {author}", language="text")
    
    if st.button("🏠 Back to Home", use_container_width=True):
        st.session_state["current_app"] = "home"
        st.rerun()
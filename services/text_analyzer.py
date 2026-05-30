# services/text_analyzer.py
import streamlit as st
import pandas as pd
import re
from collections import Counter

def text_analyzer():
    """App 2: Text Analyzer - word/character counts and frequency."""
    st.markdown("<h2 style='text-align: center;'>✍️ Text Analyzer</h2>", unsafe_allow_html=True)
    st.markdown("Analyze any text: count words, characters, and see top keywords.")
    
    text_input = st.text_area("Enter your text here:", height=200,
                              placeholder="Type or paste text...")
    
    if text_input:
        words = re.findall(r'\b\w+\b', text_input.lower())
        word_count = len(words)
        char_count = len(text_input)
        char_no_space = len(text_input.replace(" ", ""))
        sentences = re.split(r'[.!?]+', text_input)
        sentence_count = len([s for s in sentences if s.strip()])
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Words", word_count)
        col2.metric("Characters", char_count)
        col3.metric("Characters (no spaces)", char_no_space)
        col4.metric("Sentences", sentence_count)
        
        if word_count > 0:
            word_freq = Counter(words).most_common(10)
            st.subheader("🔝 Top 10 Most Frequent Words")
            freq_df = pd.DataFrame(word_freq, columns=["Word", "Frequency"])
            st.bar_chart(freq_df.set_index("Word"))
            st.markdown("**Word Frequency Table**")
            st.dataframe(freq_df, use_container_width=True)
    else:
        st.info("Enter some text to see analysis results.")
    
    if st.button("🏠 Back to Home", use_container_width=True):
        st.session_state["current_app"] = "home"
        st.rerun()
"""
Internationalization (i18n) service for multi-language support.
Manages language switching and translation retrieval.
"""

import json
import os
import streamlit as st
from pathlib import Path


# Get the absolute path to the translations file
TRANSLATIONS_FILE = Path(__file__).parent.parent / "config" / "translations.json"


def load_translations():
    """Load translations from JSON file."""
    if TRANSLATIONS_FILE.exists():
        with open(TRANSLATIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"en": {}, "zh": {}}


# Cache translations to avoid repeated file reads
@st.cache_data
def get_translations():
    """Get cached translations dictionary."""
    return load_translations()


def init_language():
    """Initialize language setting in session state."""
    if "language" not in st.session_state:
        st.session_state["language"] = "en"


def get_language():
    """Get current language setting."""
    init_language()
    return st.session_state["language"]


def set_language(lang):
    """Set current language."""
    if lang in ["en", "zh"]:
        st.session_state["language"] = lang


def translate(key, default=""):
    """
    Get translation for a key in the current language.
    
    Args:
        key: Translation key
        default: Default value if key not found
        
    Returns:
        Translated string or default
    """
    init_language()
    translations = get_translations()
    current_lang = get_language()
    
    # Try to get translation in current language, fallback to English, then default
    if current_lang in translations and key in translations[current_lang]:
        return translations[current_lang][key]
    elif "en" in translations and key in translations["en"]:
        return translations["en"][key]
    else:
        return default or key


def t(key, default=""):
    """Shorthand for translate()."""
    return translate(key, default)


def render_language_switcher():
    """Render language switcher in sidebar."""
    st.markdown("---")
    st.markdown(f"### 🌐 {t('language')}")
    
    current_lang = get_language()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(t('english'), use_container_width=True, 
                    key="lang_en", 
                    disabled=(current_lang == "en")):
            set_language("en")
            st.rerun()
    
    with col2:
        if st.button(t('chinese'), use_container_width=True, 
                    key="lang_zh",
                    disabled=(current_lang == "zh")):
            set_language("zh")
            st.rerun()


def get_language_badge():
    """Get current language badge for display."""
    current_lang = get_language()
    return "🇬🇧 EN" if current_lang == "en" else "🇨🇳 ZH"

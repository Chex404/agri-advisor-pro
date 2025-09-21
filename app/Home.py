import streamlit as st
import sys
import os

# Add the project root to the Python path so we can import from `utils`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.translations import TRANSLATIONS

# Initialize session state for language if it doesn't exist. This runs once.
if 'lang' not in st.session_state:
    st.session_state.lang = "en" # Default to English

# --- Language Selection in Sidebar ---
# This is the ONLY place this selectbox should be defined. Its state is saved
# to st.session_state.lang because of the `key` argument.
st.sidebar.title("⚙️ Settings")
st.sidebar.selectbox(
    label="Language / भाषा / ଭାଷା",
    options=["en", "hi", "or"],
    format_func=lambda code: {"en": "English", "hi": "हिंदी (Hindi)", "or": "ଓଡ଼ିଆ (Odia)"}[code],
    key='lang' # This key links the widget directly to st.session_state.lang
)

# Fetch the correct set of texts based on the session state
t = TRANSLATIONS[st.session_state.lang]

# --- Main Page UI ---
st.title(f"🌱 {t['app_title']}")
st.header(t['welcome_message'])
st.write(t['welcome_subheader'])


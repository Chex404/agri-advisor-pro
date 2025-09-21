import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
import pandas as pd

# Import the backend logic and translations
from src.analysis import irrigation
from utils.translations import TRANSLATIONS

# --- Get Language from Session State ---
lang_code = st.session_state.get('lang', 'en')
t = TRANSLATIONS[lang_code]

# --- UI in Selected Language ---
st.sidebar.title("⚙️ Settings")
st.sidebar.selectbox(
    label="Language / भाषा / ଭାଷା",
    options=["en", "hi", "or"],
    format_func=lambda code: {"en": "English", "hi": "हिंदी (Hindi)", "or": "ଓଡ଼ିଆ (Odia)"}[code],
    key='lang'
)


st.title("💧 " + t.get("page_irrigation_advisor", "Irrigation Advisor"))
st.write(t.get("irrigation_advisor_instruction", "Enter your farm's location to get a smart irrigation advisory."))

st.header(t.get("farm_location_header", "Enter Your Farm's Location"))
col1, col2 = st.columns(2)
with col1:
    lat = st.number_input(t.get("latitude", "Latitude"), value=20.46, format="%.4f")
with col2:
    lon = st.number_input(t.get("longitude", "Longitude"), value=85.88, format="%.4f")

if st.button(t.get("get_advice_button", "Get Irrigation Advice"), type="primary"):
    with st.spinner(t.get("analyzing_weather_spinner", "Analyzing weather data...")):
        
        # 1. Fetch weather and soil data from the backend module
        forecast_df = irrigation.get_weather_forecast_for_irrigation(lat, lon)
        soil_type = irrigation.get_soil_type_bhuvan(lat, lon)
        
        if forecast_df.empty:
            st.error(t.get("weather_fetch_error", "Could not fetch weather forecast data."))
        else:
            # 2. Get the irrigation advice
            advice_list = irrigation.get_irrigation_advice(forecast_df, soil_type)
            
            # 3. Display the results
            st.subheader(t.get("irrigation_recommendation_header", "Irrigation Recommendation"))
            for line in advice_list:
                if "HIGH PRIORITY" in line:
                    st.error(line)
                elif "MEDIUM PRIORITY" in line:
                    st.warning(line)
                else:
                    st.success(line)

            with st.expander(t.get("show_forecast_data", "Show Forecast Data")):
                st.dataframe(forecast_df)
import streamlit as st
import pandas as pd
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import the backend logic and translations
from src.analysis import weather_risk
from utils.translations import TRANSLATIONS

# --- Sidebar and Language Selection (Consistent with other pages) ---
st.sidebar.title("⚙️ Settings")
st.sidebar.selectbox(
    label="Language / भाषा / ଭାଷା",
    options=["en", "hi", "or"],
    format_func=lambda code: {"en": "English", "hi": "हिंदी (Hindi)", "or": "ଓଡ଼ିଆ (Odia)"}[code],
    key='lang'
)
lang_code = st.session_state.get('lang', 'en')
t = TRANSLATIONS[lang_code]

# --- Main Page UI ---
st.title("🚨 " + t.get("page_risk_analyzer", "Risk Analyzer"))
st.markdown(t.get("risk_analyzer_instruction", "Enter your farm's location to get a 7-day forecast and risk analysis for pests and diseases."))

st.header(t.get("farm_location_header", "Enter Your Farm's Location"))
col1, col2 = st.columns(2)
lat = col1.number_input(t.get("latitude", "Latitude"), value=20.46, format="%.4f")
lon = col2.number_input(t.get("longitude", "Longitude"), value=85.88, format="%.4f")

if st.button(t.get("get_risk_button", "Analyze Risk"), type="primary"):
    with st.spinner(t.get("analyzing_risk_spinner", "Analyzing 7-day forecast for potential risks...")):
        
        # 1. Fetch weather forecast
        forecast_df = weather_risk.get_weather_forecast_for_risk(lat, lon)
        
        if forecast_df.empty:
            st.error(t.get("risk_fetch_error", "Could not fetch weather forecast for risk analysis."))
        else:
            # 2. Analyze for risks
            risk_alerts = weather_risk.analyze_forecast_for_risk(forecast_df)
            
            # 3. Consolidate alerts for better readability
            final_alerts = weather_risk.consolidate_alerts(risk_alerts)
            
            # 4. Display the results
            st.subheader(t.get("risk_recommendation_header", "Pest & Disease Risk Alerts"))
            
            if final_alerts:
                for alert in final_alerts:
                    st.warning(alert)
            else:
                st.success(t.get("no_risk_found", "👍 No immediate high-risk conditions detected."))

            with st.expander(t.get("show_forecast_data", "Show Forecast Data")):
                st.dataframe(forecast_df)

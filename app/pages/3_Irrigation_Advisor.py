import streamlit as st
import pandas as pd
import requests
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utils.translations import TRANSLATIONS
from src.data_ingestion import smart_soil_ingestion
from src.analysis.irrigation import deduce_soil_type, get_irrigation_advice
from src.config import WEATHERAPI

# --- Sidebar and Language Selection ---
st.sidebar.title("⚙️ Settings")
st.sidebar.selectbox(
    label="Language / भाषा / ଭାଷା", options=["en", "hi", "or"],
    format_func=lambda code: {"en": "English", "hi": "हिंदी (Hindi)", "or": "ଓଡ଼ିଆ (Odia)"}[code],
    key='lang'
)
lang_code = st.session_state.get('lang', 'en')
t = TRANSLATIONS[lang_code]

# --- API Function ---
@st.cache_data(ttl=3600)
def get_weather_forecast(lat, lon, api_key):
    """Fetches weather data and uses programmatic column names."""
    base_url = "https://api.weatherapi.com/v1/forecast.json"
    params = {"key": api_key, "q": f"{lat},{lon}", "days": 5, "aqi": "no", "alerts": "no"}
    try:
        response = requests.get(base_url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        forecast_days = data.get("forecast", {}).get("forecastday", [])
        if not forecast_days: return pd.DataFrame()
        
        rows = [
            {
                "Date": pd.to_datetime(d.get("date")),
                "precipitation_sum": d.get("day", {}).get("totalprecip_mm", 0),
                "temp_celsius": d.get("day", {}).get("avgtemp_c", 0) # Corrected column name
            }
            for d in forecast_days
        ]
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"Failed to fetch weather data: {e}")
        return pd.DataFrame()

# --- Main Page UI ---
st.title("💧 " + t.get("page_irrigation_advisor", "Irrigation Advisor"))
st.markdown(t.get("irrigation_advisor_instruction", "Get a 5-day irrigation plan based on weather forecasts and soil type."))

st.header(t["farm_location_header"])
col1, col2 = st.columns(2)
lat = col1.number_input(t["latitude"], value=20.46, format="%.4f")
lon = col2.number_input(t["longitude"], value=85.88, format="%.4f")

if st.button(t.get("get_irrigation_advice_button", "Get Irrigation Advice"), type="primary"):
    with st.spinner(t["spinner_text"]):
        weather_df = get_weather_forecast(lat, lon, WEATHERAPI)
        soil_df = smart_soil_ingestion.get_smart_soil_data(lat, lon)

        # --- Display Results ---
        st.subheader(t.get("soil_data_header", "📍 Location & Soil Data"))
        if not soil_df.empty:
            deduced_type = deduce_soil_type(soil_df)
            st.write(f"**{t.get('deduced_soil_type_label', 'Deduced Soil Type')}:** {deduced_type}")
        else:
            deduced_type = "Loamy"
            st.warning(t.get("soil_data_fallback_warning", "Could not get soil data. Using 'Loamy' as default."))

        if not weather_df.empty:
            st.subheader(t.get("forecast_header", "🌦️ 5-Day Forecast"))
            
            # Create a separate DataFrame for display purposes with user-friendly names
            display_df = weather_df.rename(columns={
                "precipitation_sum": "Rainfall (mm)",
                "temp_celsius": "Temp (°C)"  # Add the renaming rule for temperature
            })
            st.dataframe(display_df.style.format({"Date": "{:%Y-%m-%d}", "Rainfall (mm)": "{:.1f}", "Temp (°C)": "{:.1f}"}))
            
            st.subheader(t["recommendations_header"])
        
            advice = get_irrigation_advice(weather_df, deduced_type)
            for line in advice:
                st.markdown(f"- {line}")
        else:
            st.error(t.get("weather_data_error", "Could not fetch weather data. Check coordinates or API key."))
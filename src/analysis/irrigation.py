import streamlit as st
import requests
import pandas as pd
from owslib.wfs import WebFeatureService
import warnings

# Suppress the UserWarning from owslib
warnings.filterwarnings("ignore", category=UserWarning, module='owslib')

# --- 1. Data Ingestion Functions ---
@st.cache_data(ttl=3600) # Cache the weather forecast for 1 hour
def get_weather_forecast_for_irrigation(lat, lon, days=5):
    """
    Fetches the 5-day weather forecast, including evapotranspiration.
    """
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_sum,evapotranspiration_et0_fao",
        "forecast_days": days
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data['daily'])
        df['time'] = pd.to_datetime(df['time'])
        return df
    except requests.exceptions.RequestException:
        return pd.DataFrame()

@st.cache_data(ttl=86400) # Cache the soil type for 24 hours
def get_soil_type_bhuvan(lat, lon):
    """
    Queries ISRO's Bhuvan API to get the soil type description.
    """
    try:
        wfs_url = "https://bhuvan-wfs.nrsc.gov.in/bhuvan/wfs"
        wfs = WebFeatureService(url=wfs_url, version='1.1.0', timeout=15)
        layer_name = 'india_soil:IND_SOIL_250K_POLY'
        response = wfs.getfeature(typename=layer_name, bbox=(lon, lat, lon, lat), outputFormat='json')
        features = pd.read_json(response.read())['features'].iloc[0]
        soil_description = features['properties']['SOIL_DECOR']
        return soil_description
    except Exception:
        return "Unknown"

# --- 2. The Irrigation Logic Engine ---
SOIL_WATER_RETENTION = {
    "loamy": "Low", "sandy": "Low", "alluvium": "Medium",
    "clay": "High", "default": "Medium"
}

def get_irrigation_advice(forecast_df, soil_type_str):
    """
    Analyzes forecast and soil type to generate irrigation advice.
    """
    soil_type_lower = soil_type_str.lower()
    retention = SOIL_WATER_RETENTION["default"]
    for key, value in SOIL_WATER_RETENTION.items():
        if key in soil_type_lower:
            retention = value
            break
            
    DRY_SPELL_DAYS = 3
    LOW_RAIN_THRESHOLD = 1.0  # mm
    HIGH_EVAP_THRESHOLD = 4.0 # mm

    if forecast_df.empty or len(forecast_df) < DRY_SPELL_DAYS:
        return ["Not enough forecast data to provide advice."]

    dry_spell_found = False
    for i in range(len(forecast_df) - DRY_SPELL_DAYS + 1):
        window = forecast_df.iloc[i:i + DRY_SPELL_DAYS]
        is_low_rain = (window['precipitation_sum'] < LOW_RAIN_THRESHOLD).all()
        is_high_evap = (window['evapotranspiration_et0_fao'] > HIGH_EVAP_THRESHOLD).all()
        
        if is_low_rain and is_high_evap:
            dry_spell_found = True
            break
            
    if dry_spell_found and retention == "Low":
        return [
            "HIGH PRIORITY: A dry, hot spell is forecast and your soil has low water retention.",
            "Recommendation: Irrigate your fields within the next 48 hours to prevent crop stress."
        ]
    elif dry_spell_found and retention == "Medium":
        return [
            "MEDIUM PRIORITY: A dry spell is forecast.",
            "Recommendation: Monitor soil moisture closely. Be prepared to irrigate."
        ]
    else:
        return ["No immediate irrigation needed. Forecast rainfall appears sufficient."]


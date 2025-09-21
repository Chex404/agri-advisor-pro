import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import re

# --- 1. Weather Forecast Data Ingestion ---
@st.cache_data(ttl=3600) # Cache for 1 hour
def get_weather_forecast_for_risk(lat, lon, days=7):
    """
    Fetches the 7-day weather forecast from the Open-Meteo API.
    """
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,relative_humidity_2m_mean,precipitation_sum",
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

# --- 2. The Risk Analysis Engine ---
def analyze_forecast_for_risk(forecast_df):
    """
    Analyzes the forecast DataFrame for predefined risk conditions.
    """
    alerts = []
    
    # Rule: Fungal Disease Risk (e.g., Common Rust)
    # Conditions: High humidity (>80%) and warm temps (>26°C) for 3 consecutive days.
    FUNGAL_TEMP_THRESHOLD = 26
    FUNGAL_HUMIDITY_THRESHOLD = 80
    CONSECUTIVE_DAYS_FOR_FUNGAL = 3

    if forecast_df.empty or len(forecast_df) < CONSECUTIVE_DAYS_FOR_FUNGAL:
        return alerts

    # Use a rolling window to check for consecutive days meeting the criteria
    for i in range(len(forecast_df) - CONSECUTIVE_DAYS_FOR_FUNGAL + 1):
        window = forecast_df.iloc[i:i + CONSECUTIVE_DAYS_FOR_FUNGAL]
        
        is_temp_high = (window['temperature_2m_max'] > FUNGAL_TEMP_THRESHOLD).all()
        is_humidity_high = (window['relative_humidity_2m_mean'] > FUNGAL_HUMIDITY_THRESHOLD).all()

        if is_temp_high and is_humidity_high:
            start_date = window['time'].iloc[0].strftime('%B %d')
            end_date = window['time'].iloc[-1].strftime('%B %d')
            alert_message = (
                f"High Risk of Fungal Disease (e.g., Common Rust) between {start_date} and {end_date}. "
                "Conditions are favorable (high temp & humidity). "
                "Recommend inspecting crops closely."
            )
            if alert_message not in alerts:
                alerts.append(alert_message)
    return alerts

def consolidate_alerts(alerts):
    """Consolidates multiple alerts into a single, more readable one."""
    if not alerts:
        return []

    pattern = re.compile(r"between (\w+\s\d+) and (\w+\s\d+)")
    all_dates = []

    for alert in alerts:
        match = pattern.search(alert)
        if match:
            start_str, end_str = match.groups()
            all_dates.append(datetime.strptime(start_str, "%B %d"))
            all_dates.append(datetime.strptime(end_str, "%B %d"))

    if not all_dates:
        return alerts

    min_date = min(all_dates)
    max_date = max(all_dates)

    start_date_str = min_date.strftime('%B %d')
    end_date_str = max_date.strftime('%B %d')

    consolidated_message = (
        f"High Risk of Fungal Disease from {start_date_str} to {end_date_str}. "
        "Conditions are favorable for a prolonged period. "
        "Recommend continuous monitoring and proactive spraying if necessary."
    )
    return [consolidated_message]
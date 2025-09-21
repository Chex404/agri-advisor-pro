import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

@st.cache_data(ttl=86400) # Cache geocoding results for a day
def geocode_location(location_name: str):
    """
    Converts a location name (e.g., "Cuttack, Odisha") into latitude and longitude.
    Returns a tuple (lat, lon) or None if not found.
    """
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": location_name, "count": 1, "language": "en", "format": "json"}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            return result.get("latitude"), result.get("longitude")
        else:
            return None, None
    except requests.exceptions.RequestException:
        return None, None

@st.cache_data(ttl=86400) # Cache rainfall results for a day
def get_historical_average_rainfall(lat: float, lon: float, years: int = 5):
    """
    Fetches the average annual rainfall for a location over the last few years.
    """
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=years * 365)
        
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "daily": "precipitation_sum"
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        df = pd.DataFrame(data['daily'])
        df['time'] = pd.to_datetime(df['time'])
        df['year'] = df['time'].dt.year
        
        # Calculate total rainfall per year, then average those totals
        annual_rainfall = df.groupby('year')['precipitation_sum'].sum()
        average_annual_rainfall = annual_rainfall.mean()
        
        return average_annual_rainfall
    except (requests.exceptions.RequestException, KeyError, IndexError):
        return 1500  # Return a reasonable default if API fails

# smart_soil_ingestion.py
import requests
import pandas as pd
from owslib.wfs import WebFeatureService

# --- TIER 1: ISRIC SoilGrids FUNCTION (from before) ---
def get_soil_data_isric(lat, lon):
    # ... (This is the same function from our previous conversation)
    # For brevity, we'll assume this function exists and works as before.
    # It should return a DataFrame with numerical values or an empty DataFrame on failure.
    print("  -> Attempting Tier 1: ISRIC SoilGrids...")
    base_url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    properties = ["phh2o", "soc", "nitrogen"]
    params = {"lon": lon, "lat": lat, "property": properties, "depth": ["0-30cm"], "value": ["mean"]}
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        soil_data = {}
        for prop in data['properties']['layers']:
            if prop['depths'][0]['values']['mean'] is not None:
                if prop['name'] == "phh2o": soil_data['ph'] = prop['depths'][0]['values']['mean'] / 10.0
                if prop['name'] == "soc": soil_data['organic_carbon_percent'] = prop['depths'][0]['values']['mean'] / 100.0
                if prop['name'] == "nitrogen": soil_data['nitrogen_percent'] = prop['depths'][0]['values']['mean'] / 1000.0
        if not soil_data: return pd.DataFrame() # Failed if no properties found
        print("  ✅ Success from Tier 1: ISRIC SoilGrids.")
        return pd.DataFrame([soil_data])
    except requests.exceptions.RequestException:
        return pd.DataFrame()

# --- TIER 2: BHUVAN API FUNCTION ---
def get_soil_type_bhuvan(lat, lon):
    """
    Queries ISRO's Bhuvan WFS API to get the soil type for a location.
    """
    print("  -> Tier 1 failed. Attempting Tier 2: Bhuvan API...")
    try:
        # Connect to the Bhuvan WFS service for Soil Survey data
        wfs_url = "https://bhuvan-wfs.nrsc.gov.in/bhuvan/wfs"
        wfs = WebFeatureService(url=wfs_url, version='1.1.0', timeout=15)
        
        # The specific layer for National Soil Survey
        layer_name = 'india_soil:IND_SOIL_250K_POLY'
        
        # Query the service to get the soil polygon for the given point
        response = wfs.getfeature(
            typename=layer_name,
            bbox=(lon, lat, lon, lat), # Bounding box is just the point
            outputFormat='json'
        )
        data = response.read()
        
        # Extract the soil type description from the JSON response
        features = pd.read_json(data)['features'].iloc[0]
        soil_description = features['properties']['SOIL_DECOR']
        print(f"  ✅ Success from Tier 2: Bhuvan. Found soil type: {soil_description}")
        return soil_description

    except Exception as e:
        print(f"  -> Bhuvan API query failed: {e}")
        return None

# --- TIER 2.5: THE LOOKUP TABLE ---
# This table maps Bhuvan's text descriptions to the numerical values our model needs.
# You can expand this with more research from agricultural websites!
BHUVAN_SOIL_LOOKUP = {
    "Deep red loamy soils": {"ph": 6.2, "nitrogen_kg_ha": 95, "phosphorus_kg_ha": 14, "potassium_kg_ha": 170, "organic_carbon_percent": 0.48},
    "Moderately deep red loamy soils": {"ph": 6.5, "nitrogen_kg_ha": 105, "phosphorus_kg_ha": 12, "potassium_kg_ha": 180, "organic_carbon_percent": 0.50},
    "Slightly acidic alluvium-derived soils": {"ph": 6.8, "nitrogen_kg_ha": 120, "phosphorus_kg_ha": 18, "potassium_kg_ha": 200, "organic_carbon_percent": 0.55},
    # Add more mappings as you discover them
}

# --- TIER 3: STATE-LEVEL AVERAGE (Our reliable fallback) ---
def get_state_average_fallback(soil_csv_file='data/odisha_soil_data1.csv'):
    print("  -> Tiers 1 & 2 failed. Using Tier 3: State-Level Average Fallback.")
    try:
        soil_df = pd.read_csv(soil_csv_file)
        numeric_cols = soil_df.select_dtypes(include='number')
        # Rename columns to match what the model expects
        averages = numeric_cols.mean().to_frame().T
        averages.columns = [col.lower().replace(' ', '_') for col in averages.columns]
        return averages
    except FileNotFoundError:
        print("  ❌ Fallback CSV file not found!")
        return pd.DataFrame()


# --- THE MAIN "SMART" FUNCTION ---
def get_smart_soil_data(lat, lon):
    """
    Tries to get soil data from APIs in a tiered approach.
    """
    print(f"\n--- Starting Smart Soil Data Ingestion for lat={lat}, lon={lon} ---")

    # 1. Try ISRIC SoilGrids
    soil_df = get_soil_data_isric(lat, lon)
    if not soil_df.empty:
        # ISRIC gives percentages, let's add placeholder kg/ha values if needed
        # This part requires careful unit conversion based on your model's needs.
        # For now, we'll assume the model can work with what ISRIC provides.
        return soil_df

    # 2. Try Bhuvan
    soil_type = get_soil_type_bhuvan(lat, lon)
    if soil_type and soil_type in BHUVAN_SOIL_LOOKUP:
        soil_data = BHUVAN_SOIL_LOOKUP[soil_type]
        return pd.DataFrame([soil_data])

    # 3. Use Fallback
    return get_state_average_fallback()

# --- Example Usage ---
if __name__ == '__main__':
    # Example coordinates for a location in Odisha (e.g., near Cuttack)
    farm_latitude = 20.4625
    farm_longitude = 85.8830
    
    # This location will likely fail Tier 1 and 2, and use the fallback
    final_soil_data = get_smart_soil_data(farm_latitude, farm_longitude)
    print("\n--- Final Soil Data Retrieved ---")
    print(final_soil_data.to_string())

    # Try a different location that might have Bhuvan data
    # farm_latitude = 28.6139 # Delhi
    # farm_longitude = 77.2090
    # final_soil_data = get_smart_soil_data(farm_latitude, farm_longitude)
    # print("\n--- Final Soil Data Retrieved ---")
    # print(final_soil_data.to_string())
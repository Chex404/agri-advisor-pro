# src/data_ingestion/smart_soil_ingestion.py

import requests
import pandas as pd
from owslib.wfs import WebFeatureService
import io

# --- TIER 1: ISRIC SoilGrids FUNCTION (Improved) ---
def get_soil_data_isric(lat, lon):
    print("  -> Attempting Tier 1: ISRIC SoilGrids...")
    base_url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    properties = ["phh2o", "soc", "nitrogen", "cec", "clay", "sand"]
    params = {
        "lon": lon,
        "lat": lat,
        "property": properties,
        "depth": ["0-30cm"],
        "value": ["mean"]
    }
    try:
        response = requests.get(base_url, params=params, timeout=15)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        
        soil_data = {}
        # Check if the 'properties' and 'layers' keys exist and are not empty
        if 'properties' in data and 'layers' in data['properties']:
            for prop in data['properties']['layers']:
                # Ensure the value is not None before processing
                if prop['depths'][0]['values']['mean'] is not None:
                    if prop['name'] == "phh2o":
                        soil_data['ph'] = round(prop['depths'][0]['values']['mean'] / 10.0, 2)
                    elif prop['name'] == "soc":
                        # Convert Soil Organic Carbon (g/kg) to Organic Carbon Percent
                        soil_data['organic_carbon_percent'] = round(prop['depths'][0]['values']['mean'] / 100.0, 2)
                    elif prop['name'] == "nitrogen":
                         # Convert Nitrogen (cg/kg) to kg/ha (approximate conversion)
                        soil_data['nitrogen_kg_ha'] = round(prop['depths'][0]['values']['mean'] * 15, 2)
        
        if not soil_data or 'ph' not in soil_data:
            print("  -> ISRIC response received, but contained no usable data for this location.")
            return pd.DataFrame()

        print("  ✅ Success from Tier 1: ISRIC SoilGrids.")
        return pd.DataFrame([soil_data])

    except requests.exceptions.Timeout:
        print("  -> ISRIC API request timed out.")
        return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        print(f"  -> ISRIC API request failed: {e}")
        return pd.DataFrame()


# --- TIER 2: BHUVAN API FUNCTION (Improved) ---
def get_soil_type_bhuvan(lat, lon):
    print("  -> Attempting Tier 2: Bhuvan API...")
    try:
        wfs_url = "https://bhuvan-wfs.nrsc.gov.in/bhuvan/wfs"
        wfs = WebFeatureService(url=wfs_url, version='1.1.0', timeout=20)
        layer_name = 'india_soil:IND_SOIL_250K_POLY'
        
        response = wfs.getfeature(
            typename=layer_name,
            bbox=(lon, lat, lon, lat),
            outputFormat='json'
        )
        # Use io.BytesIO to handle potential encoding issues
        data_bytes = io.BytesIO(response.read())
        
        # Check if response is empty
        if data_bytes.getbuffer().nbytes == 0:
            print("  -> Bhuvan returned an empty response.")
            return None
        
        df = pd.read_json(data_bytes)
        
        if 'features' in df and not df['features'].empty:
            soil_description = df['features'].iloc[0]['properties']['SOIL_DECOR']
            print(f"  ✅ Success from Tier 2: Bhuvan. Found soil type: {soil_description}")
            return soil_description
        else:
            print("  -> Bhuvan responded, but found no soil feature for this location.")
            return None

    except Exception as e:
        # This will now catch network errors like "Failed to resolve"
        print(f"  -> Bhuvan API query failed. The service may be down or your network has issues.")
        print(f"     Error details: {e}")
        return None

# --- TIER 2.5: THE LOOKUP TABLE ---
BHUVAN_SOIL_LOOKUP = {
    "Deep red loamy soils": {"ph": 6.2, "nitrogen_kg_ha": 95, "phosphorus_kg_ha": 14, "potassium_kg_ha": 170, "organic_carbon_percent": 0.48},
    "Moderately deep red loamy soils": {"ph": 6.5, "nitrogen_kg_ha": 105, "phosphorus_kg_ha": 12, "potassium_kg_ha": 180, "organic_carbon_percent": 0.50},
    "Slightly acidic alluvium-derived soils": {"ph": 6.8, "nitrogen_kg_ha": 120, "phosphorus_kg_ha": 18, "potassium_kg_ha": 200, "organic_carbon_percent": 0.55},
    # This table can be expanded with more soil types found in India.
}

# --- TIER 3: STATE-LEVEL AVERAGE (Our reliable fallback) ---
def get_state_average_fallback(soil_csv_file='data/odisha_soil_data1.csv'):
    print("  -> Tiers 1 & 2 failed. Using Tier 3: State-Level Average Fallback.")
    try:
        soil_df = pd.read_csv(soil_csv_file)
        # Ensure we only calculate mean for numeric columns
        numeric_cols = soil_df.select_dtypes(include='number')
        averages = numeric_cols.mean().to_frame().T
        # Standardize column names to match what the model expects
        averages.columns = [str(col).lower().replace(' ', '_') for col in averages.columns]
        print("  ✅ Success from Tier 3: Fallback.")
        return averages
    except FileNotFoundError:
        print(f"  ❌ Fallback CSV file not found at '{soil_csv_file}'!")
        # Return an empty dataframe with expected columns for consistency
        return pd.DataFrame(columns=['ph', 'nitrogen_kg_ha', 'phosphorus_kg_ha', 'potassium_kg_ha', 'organic_carbon_percent'])


# --- THE MAIN "SMART" FUNCTION ---
def get_smart_soil_data(lat, lon):
    print(f"\n--- Starting Smart Soil Data Ingestion for lat={lat}, lon={lon} ---")

    # 1. Try ISRIC SoilGrids
    soil_df = get_soil_data_isric(lat, lon)
    if not soil_df.empty:
        # We need to ensure all required columns are present for the model
        # If some are missing from ISRIC, we can fill them from the fallback
        fallback_df = get_state_average_fallback()
        for col in fallback_df.columns:
            if col not in soil_df.columns:
                soil_df[col] = fallback_df[col].iloc[0]
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
    # Location 1: Original Odisha coordinates (Likely to use fallback)
    print("--- Testing Location 1: Odisha ---")
    farm_latitude_odisha = 20.4625
    farm_longitude_odisha = 85.8830
    final_soil_data_1 = get_smart_soil_data(farm_latitude_odisha, farm_longitude_odisha)
    print("\n--- Final Soil Data Retrieved (Odisha) ---")
    print(final_soil_data_1.to_string())

    print("\n" + "="*50 + "\n")

    # Location 2: A location in Punjab (higher chance of API success)
    print("--- Testing Location 2: Punjab ---")
    farm_latitude_punjab = 30.80
    farm_longitude_punjab = 75.85
    final_soil_data_2 = get_smart_soil_data(farm_latitude_punjab, farm_longitude_punjab)
    print("\n--- Final Soil Data Retrieved (Punjab) ---")
    print(final_soil_data_2.to_string())
# src/analysis/irrigation.py
import pandas as pd

# --- Soil Deduction ---
def deduce_soil_type(soil_df):
    if soil_df.empty:
        return "Loamy"
    if 'potassium_kg_ha' in soil_df and soil_df['potassium_kg_ha'].iloc[0] > 190:
        return "Clay"
    if 'organic_carbon_percent' in soil_df and soil_df['organic_carbon_percent'].iloc[0] < 0.5:
        return "Sandy"
    return "Loamy"

# --- Irrigation Logic ---
SOIL_WATER_RETENTION = {
    "Loamy": "Medium",
    "Sandy": "Low",
    "Alluvium": "Medium",
    "Clay": "High"
}

def is_high_evaporation_day(day):
    return (
        day["temp_celsius"] > 30 and
        day["humidity_percent"] < 40 and
        day["wind_speed_ms"] > 3
    )

def get_irrigation_advice(forecast_df, soil_type_str):
    retention = SOIL_WATER_RETENTION.get(soil_type_str, "Medium")
    DRY_SPELL_DAYS = 3
    LOW_RAIN_THRESHOLD = 1.0

    if forecast_df.empty or len(forecast_df) < DRY_SPELL_DAYS:
        return ["Not enough forecast data to provide advice."]

    dry_spell_found = False
    for i in range(len(forecast_df) - DRY_SPELL_DAYS + 1):
        window = forecast_df.iloc[i:i + DRY_SPELL_DAYS]
        is_low_rain = (window['precipitation_sum'] < LOW_RAIN_THRESHOLD).all()
        is_high_evap = all(is_high_evaporation_day(day) for _, day in window.iterrows())

        if is_low_rain and is_high_evap:
            dry_spell_found = True
            break

    if dry_spell_found:
        if retention == "Low":
            return ["**HIGH PRIORITY:** Dry, hot spell with low-retention soil.",
                    "**Recommendation:** Irrigate within 48 hours."]
        elif retention == "Medium":
            return ["**MEDIUM PRIORITY:** A dry spell is forecast.",
                    "**Recommendation:** Monitor soil moisture and be ready to irrigate."]
        else:
            return ["**LOW PRIORITY:** Dry spell but soil retains water well.",
                    "**Recommendation:** Likely no immediate irrigation needed."]
    else:
        total_precip = forecast_df['precipitation_sum'].sum()
        return [f"No irrigation needed. Expected rainfall: **{total_precip:.2f} mm** in {len(forecast_df)} days."]

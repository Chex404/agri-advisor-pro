import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import sys
import os

# Add the project root to the Python path to find the 'src' and 'utils' folders
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import your backend functions and the translations dictionary
from src.ml import yield_predictor
from src.analysis import economics
from src.data_ingestion import smart_soil_ingestion
from utils.translations import TRANSLATIONS

# --- Helper Functions ---
def text_to_speech(text, lang='en'):
    """Converts text to an in-memory audio file."""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp
    except Exception as e:
        st.error(f"Could not generate audio. Error: {e}")
        return None

def get_soil_recommendations(soil_df, t):
    """Generates recommendations using the translation dictionary."""
    recs = []
    if soil_df['nitrogen_kg_ha'].iloc[0] < 120: recs.append(t.get("rec_urea", "Urea for Nitrogen"))
    if soil_df['phosphorus_kg_ha'].iloc[0] < 15: recs.append(t.get("rec_dap", "DAP for Phosphorus"))
    if soil_df['potassium_kg_ha'].iloc[0] < 200: recs.append(t.get("rec_mop", "MOP for Potassium"))
    if soil_df['ph'].iloc[0] < 6.0: recs.append(t.get("rec_lime", "Lime for acidic soil"))
    if not recs: return [t.get("rec_optimal", "Soil is optimal")]
    return recs

# --- Sidebar ---
st.sidebar.title("⚙️ Settings")
st.sidebar.selectbox(
    label="Language / भाषा / ଭାଷା", options=["en", "hi", "or"],
    format_func=lambda code: {"en": "English", "hi": "हिंदी (Hindi)", "or": "ଓଡ଼ିଆ (Odia)"}[code],
    key='lang'
)

# --- Get Language ---
lang_code = st.session_state.get('lang', 'en')
t = TRANSLATIONS[lang_code]

# --- Main Page UI ---
st.title("🌾 " + t["page_yield_predictor"])

# --- User Input Format ---
st.header(t.get("farm_location_header", "Step 1: Enter Your Farm's Location"))
col1, col2 = st.columns(2)
with col1:
    lat = st.number_input(t["latitude"], value=20.46, format="%.4f")
with col2:
    lon = st.number_input(t["longitude"], value=85.88, format="%.4f")

st.header(t.get("crop_details_header", "Step 2: Enter Crop & Farming Details"))
col3, col4, col5 = st.columns(3)
with col3:
    crop = st.selectbox(t["select_crop"], ["Rice", "Maize", "Jowar", "Wheat", "Sugarcane", "Masoor"])
with col4:
    season = st.selectbox(t["select_season"], ["Kharif", "Rabi", "Summer", "Whole Year"])
with col5:
    area = st.number_input(t["area_hectares"], value=1.0, min_value=0.1)

annual_rainfall = st.slider(t["rainfall_slider"], 500, 3500, 1500)


# --- Button and Backend Processing ---
if st.button(t["predict_button"], type="primary"):
    with st.spinner(t.get("spinner_text", "Analyzing...")):
        # 1. Get soil data using the provided lat/lon
        soil_df = smart_soil_ingestion.get_smart_soil_data(lat=lat, lon=lon)

        if soil_df.empty:
            st.error(t["soil_data_error"])
            st.stop()

        # 2. Load model and make prediction
        model_payload = yield_predictor.load_model_payload()
        input_data = pd.DataFrame({
            'crop': [crop], 'season': [season], 'area': [area], 'annual_rainfall': [annual_rainfall],
            'ph': [soil_df['ph'].iloc[0]], 'nitrogen_kg_ha': [soil_df['nitrogen_kg_ha'].iloc[0]],
            'phosphorus_kg_ha': [soil_df['phosphorus_kg_ha'].iloc[0]], 'potassium_kg_ha': [soil_df['potassium_kg_ha'].iloc[0]],
            'organic_carbon_percent': [soil_df['organic_carbon_percent'].iloc[0]]
        })
        predicted_yield = yield_predictor.make_prediction(input_data, model_payload)

        # 3. Get translated recommendations and economic analysis by passing 't'
        recommendations = get_soil_recommendations(soil_df, t)
        profit_analysis = economics.calculate_profitability(recommendations, predicted_yield, crop, t)

        # 4. Display Results
        st.success(t["predicted_yield_success"].format(pred_yield=predicted_yield))

        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.subheader(t["recommendations_header"])
            for rec in recommendations:
                st.markdown(f"- {rec}")
        with res_col2:
            st.subheader(t["economics_header"])
            st.json(profit_analysis)

        st.subheader(t["listen_button"])
        recommendations_text = ", ".join(recommendations)
        summary_text_for_audio = t["audio_summary"].format(pred_yield=predicted_yield, recommendations=recommendations_text)

        audio_file = text_to_speech(summary_text_for_audio, lang=lang_code)
        if audio_file:
            st.audio(audio_file, format='audio/mp3')


#let it be shown  
import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

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

def get_soil_recommendation_keys(soil_df):
    """Generates a list of recommendation keys based on soil data."""
    keys = []
    if soil_df['nitrogen_kg_ha'].iloc[0] < 120: keys.append("rec_urea")
    if soil_df['phosphorus_kg_ha'].iloc[0] < 15: keys.append("rec_dap")
    if soil_df['potassium_kg_ha'].iloc[0] < 200: keys.append("rec_mop")
    if soil_df['ph'].iloc[0] < 6.0: keys.append("rec_lime")
    return keys if keys else ["rec_optimal"]

# --- Sidebar and Language Selection ---
st.sidebar.title("⚙️ Settings")
st.sidebar.selectbox(
    label="Language / भाषा / ଭାଷା", options=["en", "hi", "or"],
    format_func=lambda code: {"en": "English", "hi": "हिंदी (Hindi)", "or": "ଓଡ଼ିଆ (Odia)"}[code],
    key='lang'
)

lang_code = st.session_state.get('lang', 'en')
t = TRANSLATIONS[lang_code]

# --- Main Page UI ---
st.title("🌾 " + t["page_yield_predictor"])

st.header(t["farm_location_header"])
col1, col2 = st.columns(2)
with col1:
    lat = st.number_input(t["latitude"], value=20.46, format="%.4f")
with col2:
    lon = st.number_input(t["longitude"], value=85.88, format="%.4f")

st.header(t["crop_details_header"])
col3, col4, col5 = st.columns(3)
with col3:
    # Use keys for logic but display translated values
    crop_options = list(t["crops"].keys())
    crop = st.selectbox(t["select_crop"], options=crop_options, format_func=lambda key: t["crops"][key])
with col4:
    season_options = list(t["seasons"].keys())
    season = st.selectbox(t["select_season"], options=season_options, format_func=lambda key: t["seasons"][key])
with col5:
    area = st.number_input(t["area_hectares"], value=1.0, min_value=0.1)

annual_rainfall = st.slider(t["rainfall_slider"], 500, 3500, 1500)

# --- Button and Backend Processing ---
if st.button(t["predict_button"], type="primary"):
    with st.spinner(t["spinner_text"]):
        soil_df = smart_soil_ingestion.get_smart_soil_data(lat=lat, lon=lon)

        if soil_df.empty:
            st.error(t["soil_data_error"])
            st.stop()

        model_payload = yield_predictor.load_model_payload()
        input_data = pd.DataFrame({
            'crop': [crop], 'season': [season], 'area': [area], 'annual_rainfall': [annual_rainfall],
            'ph': [soil_df['ph'].iloc[0]], 'nitrogen_kg_ha': [soil_df['nitrogen_kg_ha'].iloc[0]],
            'phosphorus_kg_ha': [soil_df['phosphorus_kg_ha'].iloc[0]], 'potassium_kg_ha': [soil_df['potassium_kg_ha'].iloc[0]],
            'organic_carbon_percent': [soil_df['organic_carbon_percent'].iloc[0]]
        })
        predicted_yield = yield_predictor.make_prediction(input_data, model_payload)

        # Get recommendation keys and then get translated results
        recommendation_keys = get_soil_recommendation_keys(soil_df)
        profit_analysis = economics.calculate_profitability(recommendation_keys, predicted_yield, crop, t)
        
        # --- Display Results ---
        st.success(t["predicted_yield_success"].format(pred_yield=predicted_yield))

        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.subheader(t["recommendations_header"])
            for key in recommendation_keys:
                st.markdown(f"- {t.get(key, key)}") # Display translated recommendation
        with res_col2:
            st.subheader(t["economics_header"])
            for label, value in profit_analysis.items():
                st.markdown(f"**{label}:** {value}") # Display formatted, translated analysis

        # --- Audio Summary ---
        st.subheader(t["listen_button"])
        recommendations_text = ", ".join([t.get(key, key) for key in recommendation_keys])
        summary_text_for_audio = t["audio_summary"].format(pred_yield=predicted_yield, recommendations=recommendations_text)

        audio_file = text_to_speech(summary_text_for_audio, lang=lang_code)
        if audio_file:
            st.audio(audio_file, format='audio/mp3')
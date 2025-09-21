import streamlit as st
from PIL import Image
import tensorflow as tf
import numpy as np
import sys
import os

# Add the project root to the Python path to find the 'src' and 'utils' folders
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import the translations dictionary
from utils.translations import TRANSLATIONS

# --- Model Loading with Caching ---
@st.cache_resource
def load_pest_model():
    """Loads the saved pest detection model from disk."""
    try:
        model = tf.keras.models.load_model('models/pest_classifier_model.h5')
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

# --- Get Language from Session State ---
# READS the language set in Home.py, does NOT create a new selectbox.
lang_code = st.session_state.get('lang', 'en')
t = TRANSLATIONS[lang_code]

# --- Main Page UI in Selected Language ---
st.sidebar.title("⚙️ Settings")
st.sidebar.selectbox(
    label="Language / भाषा / ଭାଷା",
    options=["en", "hi", "or"],
    format_func=lambda code: {"en": "English", "hi": "हिंदी (Hindi)", "or": "ଓଡ଼ିଆ (Odia)"}[code],
    key='lang'
)

st.title(t["pest_detector_title"])
st.write(t["pest_detector_instruction"])

# --- Class Labels (must match folder names) ---
class_names = ['Corn_(maize)___Common_rust', 'Corn_(maize)___healthy']

# --- File Uploader and Prediction ---
uploaded_file = st.file_uploader(t["file_uploader_label"], type=["jpg", "jpeg", "png"])
model = load_pest_model()

if uploaded_file is not None and model is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)
    
    with st.spinner(t["classifying_text"]):
        # Preprocess the image
        img_array = np.array(image.resize((224, 224))) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        # Make prediction
        predictions = model.predict(img_array)
        score = tf.nn.softmax(predictions[0])
        
        # Display result
        predicted_class = class_names[np.argmax(score)].replace('___', ' ').replace('_', ' ')
        confidence = 100 * np.max(score)
        
        st.success(t["result_text"].format(result=predicted_class))
        st.info(t["confidence_text"].format(confidence=confidence))


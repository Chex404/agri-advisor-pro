import streamlit as st
from PIL import Image
import tensorflow as tf
import numpy as np
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from utils.translations import TRANSLATIONS

# --- Sidebar and Language Selection (Consistent with other pages) ---
st.sidebar.title("⚙️ Settings")
st.sidebar.selectbox(
    label="Language / भाषा / ଭାଷା", options=["en", "hi", "or"],
    format_func=lambda code: {"en": "English", "hi": "हिंदी (Hindi)", "or": "ଓଡ଼ିଆ (Odia)"}[code],
    key='lang'
)
lang_code = st.session_state.get('lang', 'en')
t = TRANSLATIONS[lang_code]

# --- Load Model and Class Names ---
@st.cache_resource
def load_resources():
    """Loads the ML model and class names, caching them to improve performance."""
    model = tf.keras.models.load_model('models/pest_classifier_model.h5')
    
    try:
        with open('models/pest_class_names.json', 'r') as f:
            class_names = json.load(f)
    except FileNotFoundError:
        # Fallback if the JSON file doesn't exist
        class_names = ['Corn_(maize)___Common_rust', 'Corn_(maize)___healthy']
    return model, class_names

try:
    model, class_names = load_resources()
except Exception as e:
    st.error(f"Error loading model resources: {e}")
    st.info("Please ensure 'pest_classifier_model.h5' exists in the 'models/' directory.")
    st.stop()

# --- Main Page UI ---
st.title("🌿 " + t["pest_detector_title"])
st.markdown(t["pest_detector_instruction"])

uploaded_file = st.file_uploader(t["file_uploader_label"], type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    # Use the translated caption
    st.image(image, caption=t.get("uploaded_image_caption", "Uploaded Image."), use_column_width=True)

    with st.spinner(t["classifying_text"]):
        # Preprocess the image
        img_resized = image.resize((224, 224))
        img_array = np.array(img_resized) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Make prediction
        predictions = model.predict(img_array)
        score = tf.nn.softmax(predictions[0])

        # Display result using translated text
        predicted_class_key = class_names[np.argmax(score)]
    
        predicted_class_display = predicted_class_key.replace('___', ' ').replace('_', ' ')
        confidence = 100 * np.max(score)

        st.success(t["result_text"].format(result=predicted_class_display))
        st.info(t["confidence_text"].format(confidence=confidence))
else:
    # Add a placeholder text for when no file is uploaded
    st.info(t.get("pest_detector_placeholder", "Please upload an image of a crop leaf to begin analysis."))

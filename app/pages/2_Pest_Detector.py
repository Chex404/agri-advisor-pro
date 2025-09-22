# app/pages/2_Pest_Detector.py

import streamlit as st
from PIL import Image
import tensorflow as tf
import numpy as np
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from utils.translations import TRANSLATIONS

# --- Language and Translation Setup ---
lang_code = st.session_state.get('lang', 'en')
t = TRANSLATIONS[lang_code]

# --- Load Model ---
# Use a try-except block to handle potential errors during model loading
try:
    # It's good practice to cache the model to avoid reloading it on every interaction
    @st.cache_resource
    def load_pest_model():
        model = tf.keras.models.load_model('models/pest_classifier_model.h5')
        return model
    
    model = load_pest_model()
except Exception as e:
    st.error(f"Error loading model: {e}")
    st.info("Please ensure the model file 'models/pest_classifier_model.h5' exists.")
    st.stop()
    
# --- Class Labels (Must match the folder names used during training) ---
class_names = ['Corn_(maize)___Common_rust', 'Corn_(maize)___healthy']

# --- UI ---
st.title(t["pest_detector_title"])
st.write(t["pest_detector_instruction"])

uploaded_file = st.file_uploader(t["file_uploader_label"], type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)
    
    with st.spinner(t["classifying_text"]):
        # Preprocess the image to fit the model's input requirements
        img_resized = image.resize((224, 224))
        img_array = np.array(img_resized) / 255.0
        img_array = np.expand_dims(img_array, axis=0) # Add batch dimension
        
        # Make prediction
        predictions = model.predict(img_array)
        score = tf.nn.softmax(predictions[0])
        
        # Display result using translated text
        predicted_class = class_names[np.argmax(score)].replace('___', ' ').replace('_', ' ')
        confidence = 100 * np.max(score)
        
        st.success(t["result_text"].format(result=predicted_class))
        st.info(t["confidence_text"].format(confidence=confidence))
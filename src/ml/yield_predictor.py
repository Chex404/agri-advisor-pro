import joblib
import pandas as pd

# Path to your saved model
MODEL_PATH = "models/crop_yield_model.joblib"

def load_model_payload():
    """Loads the saved model and its associated column data."""
    return joblib.load(MODEL_PATH)

def make_prediction(input_df, model_payload):
    """Uses the loaded model to make a yield prediction."""
    model = model_payload["model"]
    model_columns = model_payload["columns"]

    # Ensure the input data has the same columns as the training data
    input_processed = pd.get_dummies(input_df)
    input_processed = input_processed.reindex(columns=model_columns, fill_value=0)

    prediction = model.predict(input_processed)
    return prediction[0]

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import warnings
import joblib

# Import the functions we need from other files
from src.data_ingestion.smart_soil_ingestion import get_state_average_fallback

# --- CONFIGURATION & SETUP ---
warnings.filterwarnings('ignore')
CROP_DATA_FILE = 'data/crop_yield.csv'

# ==============================================================================
# PART 1: DATA PREPARATION FUNCTION
# ==============================================================================

def prepare_training_data(location_soil_data):
    """
    Loads historical crop data and injects the location-specific soil data.
    """
    print("\n--- 2. Preparing Training Data ---")
    try:
        crop_df = pd.read_csv(CROP_DATA_FILE)
    except FileNotFoundError:
        print(f"❌ ERROR: Could not find '{CROP_DATA_FILE}'.")
        return None
    
    # Filter for a specific state if needed, e.g., Odisha
    state_crop_df = crop_df[crop_df['State'] == 'Odisha'].copy()
    state_crop_df.columns = state_crop_df.columns.str.lower().str.replace(' ', '_')
    
    # Inject the fetched soil data into every row
    for col in location_soil_data.columns:
        if col in state_crop_df.columns:
            state_crop_df.drop(columns=[col], inplace=True)
        state_crop_df[col] = location_soil_data[col].iloc[0]

    state_crop_df.dropna(inplace=True)
    print("✅ Historical data injected with location-specific soil properties.")
    return state_crop_df

# ==============================================================================
# PART 2: MODEL TRAINING FUNCTION
# ==============================================================================

def train_model(df):
    """
    Trains the RandomForestRegressor model and returns the model and its columns.
    """
    print("\n--- 3. Training AI Model ---")
    features = ['area', 'annual_rainfall', 'ph', 'nitrogen_kg_ha', 'phosphorus_kg_ha', 'potassium_kg_ha', 'organic_carbon_percent', 'crop', 'season']
    target = 'yield'
    
    for col in features:
        if col not in df.columns:
            print(f"❌ ERROR: Missing required column '{col}' in the dataset.")
            return None, None

    X_raw = df[features]
    y = df[target]
    
    # One-hot encode categorical features
    X = pd.get_dummies(X_raw, columns=['crop', 'season'], drop_first=True)
    
    # Get the column names AFTER one-hot encoding
    trained_columns = X.columns
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    print("✅ Model training complete.")
    
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    print(f" 	-> Model R-squared (R²): {r2:.4f}")
    
    # Return the trained model AND the list of columns it was trained on
    return model, trained_columns

# ==============================================================================
# PART 3: MAIN EXECUTION BLOCK
# ==============================================================================
if __name__ == "__main__":
    print("--- Preparing data for model training ---")
    soil_data = get_state_average_fallback()

    if not soil_data.empty:
        training_df = prepare_training_data(soil_data)
        
        if training_df is not None:
            # Call the training function and receive the model and columns
            model, trained_columns = train_model(training_df)
            
            # Now, create the payload and save it
            if model and trained_columns is not None:
                model_payload = {"model": model, "columns": list(trained_columns)}
                
                joblib.dump(model_payload, 'models/crop_yield_model.joblib')
                
                print("\n✅✅✅")
                print("Model training successful.")
                print("Saved to 'models/crop_yield_model.joblib'")
                print("✅✅✅")
            else:
                print("\n❌ CRITICAL ERROR: Model training failed. Model not saved.")
    else:
        print("\n❌ CRITICAL ERROR: Could not load soil data for training. Aborting.")
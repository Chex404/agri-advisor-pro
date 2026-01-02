
# Agri-Advisor Pro

**An AI-powered decision support system for modern, data-driven agriculture.**

## Overview

Agri-Advisor Pro is an intelligent farming assistant designed to empower farmers by providing actionable, data-driven insights. By leveraging machine learning, real-time data APIs, and agronomic principles, this tool helps optimize resource usage, mitigate risks, and enhance crop profitability. Our goal is to bridge the gap between traditional farming practices and modern technology, making advanced analytics accessible to every farmer.

This application provides critical advice on **crop yield prediction**, **pest and disease detection**, **smart irrigation scheduling**, and **proactive risk analysis** through a user-friendly, multilingual interface.

-----

## Features

  * **AI-Powered Yield Prediction:**

      * Estimates crop yield (in tonnes/hectare) based on location, soil health, weather patterns, and crop choice.
      * Provides a detailed **economic analysis**, including estimated input costs, revenue, and net profit.
      * Features a **Text-to-Speech** option to read out the summary in the user's selected language.

  * **Instant Pest & Disease Detection:**

      * Utilizes a Convolutional Neural Network (CNN) to identify common plant diseases from uploaded leaf images.
      * Provides immediate classification (e.g., "Corn Common Rust" or "Healthy") with a confidence score.

  * **Smart Irrigation Advisor:**

      * Fetches a 5-day weather forecast for the farm's precise location.
      * Analyzes predicted rainfall and temperature, combined with the deduced soil type, to provide a clear, daily irrigation plan.

  * **Proactive Risk Analysis:**

      * Analyzes a 7-day weather forecast to identify conditions favorable for the outbreak of common pests and fungal diseases.
      * Issues timely alerts, allowing farmers to take preventative measures before an infestation occurs.

  * **Multi-Language Support:**

      * Fully functional interface available in **English**, **हिंदी (Hindi)**, and **ଓଡ଼ିଆ (Odia)** to ensure broad accessibility.

  * **Dynamic Soil Data Ingestion:**

      * A robust, tiered system fetches the most accurate soil data available for any given latitude and longitude.
      * **Tier 1:** Queries the global ISRIC SoilGrids API for detailed soil properties.
      * **Tier 2:** If ISRIC fails, it queries India-specific Bhuvan API for soil classification.
      * **Tier 3:** As a final fallback, it uses reliable state-level average data from a local CSV file.

-----

##  Tech Stack

  * **Frontend (MVP):** **Streamlit** - For rapid development and creating an interactive data application.
  * **Backend & Data Science:** **Python**, Pandas, Scikit-learn, TensorFlow/Keras
  * **Data Sources & APIs:** ISRIC SoilGrids, Bhuvan WFS, Open-Meteo / WeatherAPI.com
  * **Future Vision:** The current MVP is built with Streamlit for rapid prototyping. The long-term vision is to migrate the frontend to **React Native** for a scalable, cross-platform, and mobile-first solution.

-----

## Project Structure

```
AGRI-ADVISOR-PRO/
│
├── app/                          # Streamlit application (UI layer)
│   ├── pages/
│   │   ├── 1_Yield_Predictor.py
│   │   ├── 2_Pest_Detector.py
│   │   ├── 3_Irrigation_Advisor.py
│   │   └── 4_Risk_Analyzer.py
│   ├── utils/
│   │   └── translations.py
│   └── Home.py
│
├── data/
│   ├── crop_yield.csv
│   └── odisha_soil_data1.csv
│
├── models/
│   ├── crop_yield_model.joblib
│   └── pest_classifier_model.h5
│
├── pest_img_data/                # Training data for pest model
│
├── src/
│   ├── analysis/
│   │   ├── economics.py
│   │   ├── irrigation.py
│   │   ├── location_services.py
│   │   └── weather_risk.py
│   │
│   ├── data_ingestion/
│   │   └── smart_soil_ingestion.py
│   │
│   ├── ml/
│   │   ├── train_pest_model.py
│   │   ├── train_yield_model.py
│   │   └── yield_predictor.py
│   │
│   └── config.py
│
├── requirements.txt
├── README.md
└── .gitignore

```

-----

##  Getting Started

### Prerequisites

  * Python 3.8+
  * An API key from a weather provider (e.g., [WeatherAPI.com](https://www.weatherapi.com/))

### Installation & Usage

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/AGRI-ADVISOR-PRO.git
    cd AGRI-ADVISOR-PRO
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Add your API Key:**

      * Create a file named `config.py` inside the `src/` directory.
      * Add your weather API key to the file like this:
        ```python
        # src/config.py
        WEATHERAPI = "YOUR_API_KEY_HERE"
        ```

5.  **Run the application:**

    ```bash
    streamlit run Home.py
    ```

    The application will now be running in your browser\!

-----

##  Roadmap

#### Version 1.0 (Completed)

  * [x] Core Yield Prediction Engine with Economic Analysis
  * [x] CNN-based Pest & Disease Detection Module
  * [x] 5-Day Forecast-based Irrigation Advisor
  * [x] 7-Day Weather Risk Analyzer
  * [x] Multilingual Support (English, Hindi, Odia)

#### Future Plans

  * **Mobile Application:** Migrate the frontend from Streamlit to **React Native** for a native mobile experience.
  * **Model Expansion:** Train the models on a wider variety of crops and plant diseases to increase coverage.
  * **Real-time Market Data:** Integrate APIs to fetch live market prices for more accurate profitability analysis.
  * **User Authentication:** Implement user accounts to save farm locations and track historical predictions and advice.
  * **Satellite & Drone Imagery:** Incorporate analysis of satellite or drone imagery for precision farming insights.

-----

##  Contributing

Contributions are welcome\! If you have suggestions for improvements or want to report a bug, please feel free to:

1.  Fork the repository.
2.  Create a new feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

Please open an issue first to discuss any major changes you would like to make.

-----

## ⚖️ License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

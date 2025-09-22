# src/analysis/economics.py
import pandas as pd

# Approximate costs and prices (INR)
FERTILIZER_COSTS = {
    'rec_urea': 268,   # Price per 45kg bag, assume ~45kg/hectare
    'rec_dap': 1350,   # Price per 50kg bag, assume ~50kg/hectare
    'rec_mop': 1700,   # Price per 50kg bag, assume ~50kg/hectare
    'rec_lime': 500    # Generic cost for liming
}

MARKET_PRICES = {
    'Rice': 21830, 'Maize': 20900, 'Jowar': 31800,
    'Wheat': 22750, 'Sugarcane': 3150, 'Masoor': 60000
}
DEFAULT_PRICE = 20000

def calculate_profitability(recommendation_keys, predicted_yield, crop, t):
    """
    Calculates the estimated profitability based on recommendations and yield.
    Args:
        recommendation_keys (list): A list of recommendation keys (e.g., ['rec_urea', 'rec_dap']).
        predicted_yield (float): The predicted yield in tonnes per hectare.
        crop (str): The name of the crop.
        t (dict): The translation dictionary for the selected language.
    Returns:
        dict: A dictionary containing the translated economic analysis.
    """
    # Calculate total input cost from recommended fertilizers
    input_cost = sum(FERTILIZER_COSTS.get(key, 0) for key in recommendation_keys)
    
    # Get the translated list of applied fertilizers
    applied_fertilizers = [t.get(key, key) for key in recommendation_keys]
    if not applied_fertilizers:
        applied_fertilizers = [t.get("rec_optimal", "None")]

    # Get market price and calculate revenue
    market_price = MARKET_PRICES.get(crop, DEFAULT_PRICE)
    revenue = predicted_yield * market_price
    
    # Calculate profit
    profit = revenue - input_cost

    # Build the final dictionary with TRANSLATED keys
    analysis = {
        t["econ_applied_fertilizers"]: ", ".join(applied_fertilizers),
        t["econ_input_cost"]: f"₹{input_cost:,.2f}",
        t["econ_predicted_yield"]: f"{predicted_yield:.2f} tonnes/ha",
        t["econ_market_price"]: f"₹{market_price:,.2f} /tonne",
        t["econ_revenue"]: f"₹{revenue:,.2f}",
        t["econ_profit"]: f"₹{profit:,.2f}"
    }
    
    return analysis
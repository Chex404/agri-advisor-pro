# Average cost of fertilizers per hectare for a typical dose
FERTILIZER_COSTS = {
    "urea": 2000,      # Cost in INR per hectare
    "dap": 2500,       # Diammonium Phosphate
    "mop": 1800,       # Muriate of Potash
    "lime": 1500       # For soil acidity
}

# Average Minimum Support Price (MSP) for crops in INR per tonne
CROP_MARKET_PRICES = {
    "Rice": 21830,
    "Jowar": 31800,
    "Masoor": 60000,
    "Niger seed": 75000,
    "Wheat": 22750,
    "Maize": 20900,
    "Sugarcane": 3150, # Note: Price is often per quintal, model is in tonnes
    "Default": 35000 # Average for other crops
}

def calculate_profitability(recommendations, predicted_yield, crop_name, t):
    """
    Calculates the estimated cost, revenue, and profit based on recommendations.
    Uses the translation dictionary 't' for the output keys.
    """
    total_cost = 0
    applied_fertilizers = []
    
    # Use English keywords to check recommendations, but use translated text for display
    for item in recommendations:
        item_lower = item.lower() # Check against the translated lowercase string
        
        # We need to check if the English keyword is in the recommendation value from the dict
        if "urea" in t.get("rec_urea", "urea").lower() and t.get("rec_urea", "urea") in recommendations:
             if "Urea" not in applied_fertilizers:
                total_cost += FERTILIZER_COSTS["urea"]
                applied_fertilizers.append("Urea")
        if "dap" in t.get("rec_dap", "dap").lower() and t.get("rec_dap", "dap") in recommendations:
            if "DAP" not in applied_fertilizers:
                total_cost += FERTILIZER_COSTS["dap"]
                applied_fertilizers.append("DAP")
        if "mop" in t.get("rec_mop", "mop").lower() and t.get("rec_mop", "mop") in recommendations:
            if "Muriate of Potash (MOP)" not in applied_fertilizers:
                total_cost += FERTILIZER_COSTS["mop"]
                applied_fertilizers.append("Muriate of Potash (MOP)")
        if "lime" in t.get("rec_lime", "lime").lower() and t.get("rec_lime", "lime") in recommendations:
            if "Lime" not in applied_fertilizers:
                total_cost += FERTILIZER_COSTS["lime"]
                applied_fertilizers.append("Lime")

    market_price = CROP_MARKET_PRICES.get(crop_name, CROP_MARKET_PRICES["Default"])
    total_revenue = predicted_yield * market_price
    net_profit = total_revenue - total_cost

    # Use the 't' dictionary to get the translated keys for the output
    economics_summary = {
        t.get("econ_applied_fertilizers", "Applied Fertilizers"): ", ".join(applied_fertilizers),
        t.get("econ_input_cost", "Estimated Input Cost (INR/hectare)"): f"{total_cost:,.2f}",
        t.get("econ_predicted_yield", "Predicted Yield (tonnes/hectare)"): f"{predicted_yield:.2f}",
        t.get("econ_market_price", "Market Price (INR/tonne)"): f"{market_price:,.2f}",
        t.get("econ_revenue", "Estimated Revenue (INR/hectare)"): f"{total_revenue:,.2f}",
        t.get("econ_profit", "Estimated Net Profit (INR/hectare)"): f"{net_profit:,.2f}"
    }
    
    return economics_summary


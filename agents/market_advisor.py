import json

class MarketAdvisor:
    def __init__(self, crops_data_path: str = "data/crops.json"):
        with open(crops_data_path, 'r') as f:
            self.crops_data = json.load(f)

    def calculate_profit(self, crop_key: str, farm_size_acres: float = 1.0):
        crop_data = self.crops_data.get(crop_key)
        if not crop_data: return {}
        plants_needed = crop_data["plants_per_acre"] * farm_size_acres
        investment = plants_needed * crop_data["cost_per_plant_rupees"]
        expected_yield = crop_data["yield_per_plant"] * plants_needed
        revenue = expected_yield * crop_data["market_price_per_unit_rupees"]
        profit = revenue - investment
        profit_margin = (profit / revenue * 100) if revenue > 0 else 0
        return {"crop_name": crop_data["name"], "crop_key": crop_key, "revenue_rupees": round(revenue, 2), "investment_rupees": round(investment, 2), "profit_rupees": round(profit, 2), "profit_margin_percentage": round(profit_margin, 2), "market_price_per_unit": crop_data["market_price_per_unit_rupees"], "expected_yield_units": crop_data["yield_units"]}

    def normalize_profit_scores(self, crops):
        if not crops: return {}
        profits = [self.calculate_profit(crop)["profit_rupees"] for crop in crops.keys()]
        if not profits: return {}
        min_profit = min(profits)
        max_profit = max(profits)
        profit_range = max_profit - min_profit
        scored_crops = {}
        for crop_key in crops.keys():
            profit_data = self.calculate_profit(crop_key)
            score = ((profit_data["profit_rupees"] - min_profit) / profit_range) * 10 if profit_range > 0 else 5
            scored_crops[crop_key] = {"profit_score": round(score, 2), "profit_rupees": profit_data["profit_rupees"], "crop_name": profit_data["crop_name"], "profit_margin_percentage": profit_data["profit_margin_percentage"]}
        return scored_crops

    def assess_market_demand(self, crop_key: str) -> str:
        crop_data = self.crops_data.get(crop_key)
        if not crop_data: return "MEDIUM"
        profit = crop_data["expected_profit_per_acre_rupees"]
        return "HIGH" if profit > 100000 else ("MEDIUM" if profit > 50000 else "LOW")

    def analyze(self, crops, farm_size_acres: float = 1.0):
        profit_analysis = {}
        for crop_key in crops.keys():
            profit_analysis[crop_key] = self.calculate_profit(crop_key, farm_size_acres)
        profit_scores = self.normalize_profit_scores(crops)
        for crop_key in profit_scores:
            profit_scores[crop_key]["market_demand"] = self.assess_market_demand(crop_key)
        most_profitable = max(profit_scores.items(), key=lambda x: x[1]["profit_score"]) if profit_scores else None
        return {"profit_analysis": profit_analysis, "profit_scores": profit_scores, "most_profitable": {"crop": most_profitable[0], "score": most_profitable[1]["profit_score"], "profit_rupees": most_profitable[1]["profit_rupees"]} if most_profitable else None, "farm_size_acres": farm_size_acres}

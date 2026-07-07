import json

class CropPlanner:
    def __init__(self, crops_data_path: str = "data/crops.json"):
        with open(crops_data_path, 'r') as f:
            self.crops_data = json.load(f)

    def filter_by_season(self, season: str):
        filtered = {}
        for crop_key, crop_data in self.crops_data.items():
            if season.lower() in [s.lower() for s in crop_data["best_season"]]:
                filtered[crop_key] = crop_data
        return filtered

    def filter_by_soil(self, crops, soil_type: str):
        filtered = {}
        for crop_key, crop_data in crops.items():
            if soil_type.lower() in [s.lower() for s in crop_data["soil_type"]]:
                filtered[crop_key] = crop_data
        return filtered

    def filter_by_budget(self, crops, budget: float, farm_size_acres: float = 1.0):
        filtered = {}
        for crop_key, crop_data in crops.items():
            total_cost = crop_data["cost_per_plant_rupees"] * crop_data["plants_per_acre"] * farm_size_acres
            if total_cost <= budget:
                filtered[crop_key] = crop_data
        return filtered

    def calculate_yield_score(self, crops):
        scored_crops = {}
        if not crops:
            return scored_crops
        max_profit = max([crop["expected_profit_per_acre_rupees"] for crop in crops.values()])
        for crop_key, crop_data in crops.items():
            profit = crop_data["expected_profit_per_acre_rupees"]
            yield_score = (profit / max_profit) * 10 if max_profit > 0 else 5
            scored_crops[crop_key] = {"name": crop_data["name"], "yield_score": round(yield_score, 2), "expected_profit": profit, "growing_cycle_days": crop_data["growing_cycle_days"]}
        return scored_crops

    def analyze(self, season: str, soil_type: str, budget: float, farm_size_acres: float = 1.0):
        crops = self.filter_by_season(season)
        crops = self.filter_by_soil(crops, soil_type)
        crops = self.filter_by_budget(crops, budget, farm_size_acres)
        scored_crops = self.calculate_yield_score(crops)
        top_crops = sorted(scored_crops.items(), key=lambda x: x[1]["yield_score"], reverse=True)[:5]
        return {"suitable_crops": scored_crops, "top_crops": [{"crop_key": k, **v} for k, v in top_crops], "filters_applied": {"season": season, "soil_type": soil_type, "budget_rupees": budget, "farm_size_acres": farm_size_acres}}

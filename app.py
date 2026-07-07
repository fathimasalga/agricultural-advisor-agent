import os
from flask import Flask, request, jsonify
import json
import logging
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Agent classes (same as in notebook)
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
        if not crops: return scored_crops
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

class DiseaseDetective:
    def __init__(self, crops_data_path: str = "data/crops.json"):
        with open(crops_data_path, 'r') as f:
            self.crops_data = json.load(f)
    def fetch_weather(self, latitude: float, longitude: float):
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {"latitude": latitude, "longitude": longitude, "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"}
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                current = data["current"]
                return {"temperature_celsius": current["temperature_2m"], "humidity_percentage": current["relative_humidity_2m"], "rainfall_mm": current["precipitation"], "wind_speed_kmh": current["wind_speed_10m"]}
            else:
                return self.get_fallback_weather()
        except Exception as e:
            return self.get_fallback_weather()
    def get_fallback_weather(self):
        return {"temperature_celsius": 27, "humidity_percentage": 75, "rainfall_mm": 5, "wind_speed_kmh": 10}
    def assess_fungal_disease_risk(self, humidity: float, temperature: float, rainfall: float) -> float:
        risk = 0
        if humidity > 80: risk += 4
        elif humidity > 70: risk += 3
        elif humidity > 60: risk += 1
        if 25 <= temperature <= 30: risk += 3
        elif 20 <= temperature <= 35: risk += 1
        if rainfall > 10: risk += 3
        elif rainfall > 5: risk += 1
        return min(risk, 10)
    def assess_bacterial_disease_risk(self, humidity: float, temperature: float, wind_speed: float) -> float:
        risk = 0
        if humidity > 80: risk += 3
        elif humidity > 70: risk += 1
        if 28 <= temperature <= 32: risk += 4
        elif 25 <= temperature <= 35: risk += 2
        if wind_speed > 15: risk += 3
        elif wind_speed > 10: risk += 1
        return min(risk, 10)
    def assess_pest_risk(self, temperature: float, humidity: float) -> float:
        risk = 0
        if temperature > 25: risk += 5
        elif temperature > 20: risk += 3
        if 60 <= humidity <= 80: risk += 5
        elif humidity > 80 or humidity < 40: risk += 2
        return min(risk, 10)
    def calculate_disease_risk(self, crop_key: str, weather):
        crop_data = self.crops_data.get(crop_key)
        if not crop_data: return 5
        fungal_susceptibility = 1.0 if crop_data["disease_risks"]["fungal"] == "high" else (0.5 if crop_data["disease_risks"]["fungal"] == "medium" else 0.2)
        bacterial_susceptibility = 1.0 if crop_data["disease_risks"]["bacterial"] == "high" else (0.5 if crop_data["disease_risks"]["bacterial"] == "medium" else 0.2)
        pest_susceptibility = 1.0 if crop_data["disease_risks"]["pest"] == "high" else (0.5 if crop_data["disease_risks"]["pest"] == "medium" else 0.2)
        fungal_risk = self.assess_fungal_disease_risk(weather["humidity_percentage"], weather["temperature_celsius"], weather["rainfall_mm"])
        bacterial_risk = self.assess_bacterial_disease_risk(weather["humidity_percentage"], weather["temperature_celsius"], weather["wind_speed_kmh"])
        pest_risk = self.assess_pest_risk(weather["temperature_celsius"], weather["humidity_percentage"])
        total_risk = (fungal_risk * fungal_susceptibility * 0.4 + bacterial_risk * bacterial_susceptibility * 0.3 + pest_risk * pest_susceptibility * 0.3)
        return round(min(total_risk, 10), 2)
    def analyze(self, crops, latitude: float, longitude: float):
        weather = self.fetch_weather(latitude, longitude)
        disease_risks = {}
        for crop_key in crops.keys():
            risk = self.calculate_disease_risk(crop_key, weather)
            disease_risks[crop_key] = {"risk_score": risk, "risk_level": "LOW" if risk < 3 else ("MEDIUM" if risk < 6 else "HIGH"), "crop_name": self.crops_data[crop_key]["name"]}
        safe_crops = [k for k, v in disease_risks.items() if v["risk_score"] < 3]
        return {"weather": weather, "disease_risks": disease_risks, "safe_crops": safe_crops, "location": {"latitude": latitude, "longitude": longitude}}

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
        if profit > 100000: return "HIGH"
        elif profit > 50000: return "MEDIUM"
        else: return "LOW"
    def analyze(self, crops, farm_size_acres: float = 1.0):
        profit_analysis = {}
        for crop_key in crops.keys():
            profit_analysis[crop_key] = self.calculate_profit(crop_key, farm_size_acres)
        profit_scores = self.normalize_profit_scores(crops)
        for crop_key in profit_scores:
            profit_scores[crop_key]["market_demand"] = self.assess_market_demand(crop_key)
        most_profitable = max(profit_scores.items(), key=lambda x: x[1]["profit_score"]) if profit_scores else None
        return {"profit_analysis": profit_analysis, "profit_scores": profit_scores, "most_profitable": {"crop": most_profitable[0], "score": most_profitable[1]["profit_score"], "profit_rupees": most_profitable[1]["profit_rupees"]} if most_profitable else None, "farm_size_acres": farm_size_acres}

class DecisionSynthesizer:
    @staticmethod
    def calculate_safety_score(disease_risk: float) -> float:
        return max(0, 10 - disease_risk)
    @staticmethod
    def synthesize_scores(crop_key: str, yield_score: float, profit_score: float, disease_risk: float):
        safety_score = DecisionSynthesizer.calculate_safety_score(disease_risk)
        final_score = (yield_score * 0.3 + profit_score * 0.4 + safety_score * 0.3)
        return {"crop_key": crop_key, "yield_score": round(yield_score, 2), "profit_score": round(profit_score, 2), "safety_score": round(safety_score, 2), "disease_risk": round(disease_risk, 2), "final_score": round(final_score, 2), "score_breakdown": {"yield_contribution": round(yield_score * 0.3, 2), "profit_contribution": round(profit_score * 0.4, 2), "safety_contribution": round(safety_score * 0.3, 2)}}
    @staticmethod
    def generate_reasoning(crop_key: str, scores, crop_name: str, profit_rupees: float, disease_risk: float) -> str:
        yield_desc = "excellent" if scores["yield_score"] > 7 else ("good" if scores["yield_score"] > 5 else "moderate")
        profit_desc = "maximum" if scores["profit_score"] > 7 else ("good" if scores["profit_score"] > 5 else "moderate")
        safety_desc = "safe" if scores["safety_score"] > 7 else ("medium risk" if scores["safety_score"] > 5 else "risky")
        reasoning = (f"{crop_name} has {yield_desc} yield potential ({scores['yield_score']}/10), {profit_desc} profit opportunity ({scores['profit_score']}/10 scoring ~{profit_rupees:,.0f} rupees), and {safety_desc} disease resistance ({scores['safety_score']}/10, disease risk {disease_risk}/10). Overall suitability score: {scores['final_score']}/10.")
        return reasoning
    @staticmethod
    def rank_crops(synthesized_crops):
        return sorted(synthesized_crops, key=lambda x: x["final_score"], reverse=True)
    @staticmethod
    def analyze(crop_planner_results, disease_detective_results, market_advisor_results, crops_data):
        synthesized_crops = []
        suitable_crops = crop_planner_results.get("suitable_crops", {})
        for crop_key in suitable_crops.keys():
            yield_score = crop_planner_results["suitable_crops"][crop_key]["yield_score"]
            disease_risk = disease_detective_results["disease_risks"][crop_key]["risk_score"]
            profit_score = market_advisor_results["profit_scores"][crop_key]["profit_score"]
            scores = DecisionSynthesizer.synthesize_scores(crop_key, yield_score, profit_score, disease_risk)
            profit_rupees = market_advisor_results["profit_analysis"][crop_key]["profit_rupees"]
            crop_name = crops_data[crop_key]["name"]
            reasoning = DecisionSynthesizer.generate_reasoning(crop_key, scores, crop_name, profit_rupees, disease_risk)
            synthesized_crops.append({**scores, "crop_name": crop_name, "reasoning": reasoning, "expected_profit_rupees": profit_rupees, "market_demand": market_advisor_results["profit_scores"][crop_key]["market_demand"]})
        ranked_crops = DecisionSynthesizer.rank_crops(synthesized_crops)
        top_crop = ranked_crops[0] if ranked_crops else None
        return {"recommendation": {"crop": top_crop["crop_name"], "crop_key": top_crop["crop_key"], "score": top_crop["final_score"], "reasoning": top_crop["reasoning"], "expected_profit": top_crop["expected_profit_rupees"], "market_demand": top_crop["market_demand"]} if top_crop else None, "ranked_crops": ranked_crops, "analysis": {"total_crops_evaluated": len(synthesized_crops), "weighting_formula": {"yield": "30%", "profit": "40%", "safety": "30%"}}}

class AgentOrchestrator:
    def __init__(self, crops_path: str = "data/crops.json", districts_path: str = "data/districts.json"):
        self.crop_planner = CropPlanner(crops_path)
        self.disease_detective = DiseaseDetective(crops_path)
        self.market_advisor = MarketAdvisor(crops_path)
        with open(districts_path, 'r') as f:
            self.districts_data = json.load(f)
        with open(crops_path, 'r') as f:
            self.crops_data = json.load(f)
    def recommend(self, district: str, season: str, budget: float, farm_size_acres: float = 1.0):
        district = district.lower().strip()
        season = season.lower().strip()
        if district not in self.districts_data:
            return {"error": f"District '{district}' not found. Available: {', '.join(self.districts_data.keys())}"}
        if budget <= 0:
            return {"error": "Budget must be positive"}
        district_data = self.districts_data[district]
        crop_planner_results = self.crop_planner.analyze(season=season, soil_type=district_data["soil_type"], budget=budget, farm_size_acres=farm_size_acres)
        if not crop_planner_results["suitable_crops"]:
            return {"error": f"No suitable crops found for {season} season in {district} with budget ₹{budget}"}
        suitable_crops = crop_planner_results["suitable_crops"]
        disease_detective_results = self.disease_detective.analyze(crops=suitable_crops, latitude=district_data["latitude"], longitude=district_data["longitude"])
        market_advisor_results = self.market_advisor.analyze(crops=suitable_crops, farm_size_acres=farm_size_acres)
        synthesizer_results = DecisionSynthesizer.analyze(crop_planner_results=crop_planner_results, disease_detective_results=disease_detective_results, market_advisor_results=market_advisor_results, crops_data=self.crops_data)
        return {"status": "success", "recommendation": synthesizer_results["recommendation"], "ranked_alternatives": synthesizer_results["ranked_crops"][:5], "input_parameters": {"district": district, "location": {"latitude": district_data["latitude"], "longitude": district_data["longitude"]}, "season": season, "budget_rupees": budget, "farm_size_acres": farm_size_acres, "soil_type": district_data["soil_type"]}, "current_weather": disease_detective_results["weather"], "analysis_details": {"crop_planner": crop_planner_results, "disease_detective": disease_detective_results, "market_advisor": market_advisor_results, "synthesis": synthesizer_results}}

orchestrator_instance = None

def initialize_orchestrator():
    global orchestrator_instance
    if orchestrator_instance is None:
        logging.info("Initializing AgentOrchestrator...")
        try:
            orchestrator_instance = AgentOrchestrator()
            logging.info("AgentOrchestrator initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize AgentOrchestrator: {e}", exc_info=True)
            raise RuntimeError(f"Orchestrator initialization failed: {e}")
    return orchestrator_instance

@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        orchestrator = initialize_orchestrator()
        data = request.json
        if not all(k in data for k in ['district', 'season', 'budget']):
            return jsonify({"error": "Missing required fields: district, season, budget"}), 400
        result = orchestrator.recommend(
            district=data.get('district'),
            season=data.get('season'),
            budget=float(data.get('budget')),
            farm_size_acres=float(data.get('farm_size_acres', 1.0))
        )
        return jsonify(result), 200
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logging.error(f"Error in /api/recommend: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    try:
        initialize_orchestrator()
        return jsonify({"status": "ok", "orchestrator_ready": True}), 200
    except Exception as e:
        logging.error(f"Health check failed: {e}", exc_info=True)
        return jsonify({"status": "degraded", "orchestrator_ready": False, "error": str(e)}), 500

@app.route('/api/districts', methods=['GET'])
def districts():
    try:
        with open('data/districts.json', 'r') as f:
            districts_data = json.load(f)
        return jsonify(list(districts_data.keys())), 200
    except Exception as e:
        logging.error(f"Error loading districts.json: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/crops', methods=['GET'])
def crops():
    try:
        with open('data/crops.json', 'r') as f:
            crops_data = json.load(f)
        return jsonify(list(crops_data.keys())), 200
    except Exception as e:
        logging.error(f"Error loading crops.json: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def info():
    return jsonify({
        "name": "Agricultural Advisor Agent",
        "version": "1.0.0",
        "description": "AI-powered crop recommendation system for Kerala farmers",
        "course": "Kaggle 5-Day AI Agents: Intensive Vibe Coding Course with Google",
        "endpoints": {
            "POST /api/recommend": "Get crop recommendation",
            "GET /api/health": "Health check",
            "GET /api/districts": "List available districts",
            "GET /api/crops": "List available crops",
            "GET /": "This info"
        }
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

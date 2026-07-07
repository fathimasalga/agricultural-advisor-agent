import json
import requests

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
        except:
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
        total_risk = fungal_risk * fungal_susceptibility * 0.4 + bacterial_risk * bacterial_susceptibility * 0.3 + pest_risk * pest_susceptibility * 0.3
        return round(min(total_risk, 10), 2)

    def analyze(self, crops, latitude: float, longitude: float):
        weather = self.fetch_weather(latitude, longitude)
        disease_risks = {}
        for crop_key in crops.keys():
            risk = self.calculate_disease_risk(crop_key, weather)
            disease_risks[crop_key] = {"risk_score": risk, "risk_level": "LOW" if risk < 3 else ("MEDIUM" if risk < 6 else "HIGH"), "crop_name": self.crops_data[crop_key]["name"]}
        safe_crops = [k for k, v in disease_risks.items() if v["risk_score"] < 3]
        return {"weather": weather, "disease_risks": disease_risks, "safe_crops": safe_crops, "location": {"latitude": latitude, "longitude": longitude}}

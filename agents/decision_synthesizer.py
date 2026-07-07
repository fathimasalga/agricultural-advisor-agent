class DecisionSynthesizer:
    @staticmethod
    def calculate_safety_score(disease_risk: float) -> float:
        return max(0, 10 - disease_risk)

    @staticmethod
    def synthesize_scores(crop_key: str, yield_score: float, profit_score: float, disease_risk: float):
        safety_score = DecisionSynthesizer.calculate_safety_score(disease_risk)
        final_score = yield_score * 0.3 + profit_score * 0.4 + safety_score * 0.3
        return {"crop_key": crop_key, "yield_score": round(yield_score, 2), "profit_score": round(profit_score, 2), "safety_score": round(safety_score, 2), "disease_risk": round(disease_risk, 2), "final_score": round(final_score, 2), "score_breakdown": {"yield_contribution": round(yield_score * 0.3, 2), "profit_contribution": round(profit_score * 0.4, 2), "safety_contribution": round(safety_score * 0.3, 2)}}

    @staticmethod
    def generate_reasoning(crop_key: str, scores, crop_name: str, profit_rupees: float, disease_risk: float) -> str:
        yield_desc = "excellent" if scores["yield_score"] > 7 else ("good" if scores["yield_score"] > 5 else "moderate")
        profit_desc = "maximum" if scores["profit_score"] > 7 else ("good" if scores["profit_score"] > 5 else "moderate")
        safety_desc = "safe" if scores["safety_score"] > 7 else ("medium risk" if scores["safety_score"] > 5 else "risky")
        return f"{crop_name} has {yield_desc} yield potential ({scores['yield_score']}/10), {profit_desc} profit opportunity ({scores['profit_score']}/10 scoring ~{profit_rupees:,.0f} rupees), and {safety_desc} disease resistance ({scores['safety_score']}/10, disease risk {disease_risk}/10). Overall suitability score: {scores['final_score']}/10."

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

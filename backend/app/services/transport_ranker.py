from app.core.config import TRANSPORT_WEIGHTS

def rank_transport_options(options: list[dict], travel_style: str, preferred_transport: list[str]) -> list[dict]:
    if not options:
        return []
    
    costs = [float(opt.get("cost", 0)) for opt in options]
    durations = [float(opt.get("duration", 0)) for opt in options]
    
    min_cost = min(costs) if costs else 0.0
    max_cost = max(costs) if costs else 1.0
    min_duration = min(durations) if durations else 0.0
    max_duration = max(durations) if durations else 1.0
    
    cost_range = max_cost - min_cost if max_cost != min_cost else 1.0
    duration_range = max_duration - min_duration if max_duration != min_duration else 1.0
    
    comfort_map = {"low": 0.2, "medium": 0.6, "high": 1.0}
    
    # Get weights based on travel style
    weights = TRANSPORT_WEIGHTS.get(travel_style, TRANSPORT_WEIGHTS.get("balanced", {"cost": 0.33, "duration": 0.33, "comfort": 0.34}))
    cost_weight = weights.get("cost", 0.33)
    duration_weight = weights.get("duration", 0.33)
    comfort_weight = weights.get("comfort", 0.34)
    
    for opt in options:
        cost = float(opt.get("cost", 0))
        duration = float(opt.get("duration", 0))
        comfort_level = str(opt.get("comfort_level", "medium")).lower()
        comfort = comfort_map.get(comfort_level, 0.5)
        
        norm_cost = 1.0 - ((cost - min_cost) / cost_range)
        norm_duration = 1.0 - ((duration - min_duration) / duration_range)
        
        base_score = (norm_cost * cost_weight) + (norm_duration * duration_weight) + (comfort * comfort_weight)
        
        transport_type = str(opt.get("type", "")).lower()
        pref_boost = 0.2 if any(pref.lower() in transport_type for pref in preferred_transport) else 0.0
        
        final_score = base_score + pref_boost
        opt["score"] = round(final_score, 4)
        opt["decision_factors"] = {
            "normalized_cost": round(norm_cost, 4),
            "normalized_duration": round(norm_duration, 4),
            "comfort_score": comfort,
            "preference_boost": pref_boost
        }
        
    return sorted(options, key=lambda x: x.get("score", 0), reverse=True)

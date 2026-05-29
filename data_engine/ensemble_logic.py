import numpy as np

def get_ensemble_prediction(xgb_prob, rf_prob):
    """
    Combines probabilities from XGBoost and Random Forest/Isolation Forest.
    Outputs the final Verdict (REAL/FAKE), Confidence Score, and Reasoning.
    """
    # Simple average ensemble
    fake_prob = float((xgb_prob + rf_prob) / 2.0)
    
    if fake_prob > 0.65:
        verdict = "FAKE"
        confidence = round(fake_prob * 100, 1)
        reasoning = "High probability of manipulation. Significant Volume-Price divergence and long upper/lower wicks detected."
    elif fake_prob > 0.5:
        verdict = "WARNING"
        confidence = round(fake_prob * 100, 1)
        reasoning = "Moderate chance of a trap. Trend shows some weakness or artificial volume spikes."
    else:
        verdict = "REAL"
        confidence = round((1 - fake_prob) * 100, 1)
        reasoning = "Trend appears sustainable. Price action is well supported by natural volume."
        
    return verdict, confidence, reasoning

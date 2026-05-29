import os
import joblib
import pandas as pd
import yfinance as yf
from data_engine.features import calculate_features
from data_engine.ensemble_logic import get_ensemble_prediction

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

_models_cache = None

def load_models():
    global _models_cache
    if _models_cache is not None:
        return _models_cache

    xgb_path = os.path.join(MODELS_DIR, 'xgboost_model.pkl')
    rf_path = os.path.join(MODELS_DIR, 'rf_model.pkl')
    scaler_path = os.path.join(MODELS_DIR, 'scaler.pkl')
    
    if not (os.path.exists(xgb_path) and os.path.exists(rf_path) and os.path.exists(scaler_path)):
        return None, None, None
        
    xgb_model = joblib.load(xgb_path)
    rf_model = joblib.load(rf_path)
    scaler = joblib.load(scaler_path)
    
    _models_cache = (xgb_model, rf_model, scaler)
    return _models_cache

def analyze_ticker(ticker_symbol: str):
    """
    Fetches the latest data, applies models, and returns verdict.
    """
    xgb_model, rf_model, scaler = load_models()
    
    if not xgb_model:
        return {"error": "Models not found. Please train the models first."}
        
    try:
        if not ticker_symbol.endswith('.NS') and not ticker_symbol.endswith('.BO'):
            ticker_symbol += '.NS'
            
        data = yf.download(ticker_symbol, period="3mo", progress=False)
        if data.empty:
            return {"error": f"No data found for {ticker_symbol}. Sirf Indian market stocks supported hain."}
            
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [c[0] for c in data.columns]
            
        data.reset_index(inplace=True)
        
        # Calculate features map
        df_features = calculate_features(data)
        
        if df_features.empty:
            return {"error": "Not enough valid data points to calculate features."}
            
        latest_data = df_features.iloc[-1:]
        
        feature_cols = ['Price_Change', 'RSI', 'Volume_Spread', 'Wick_Ratio', 'TR', 'ATR']
        X_latest = latest_data[feature_cols]
        
        X_scaled = scaler.transform(X_latest)
        
        # XGBoost handles predict_proba directly
        xgb_prob = xgb_model.predict_proba(X_scaled)[0][1]
        rf_prob = rf_model.predict_proba(X_scaled)[0][1]
        
        verdict, confidence, reasoning = get_ensemble_prediction(xgb_prob, rf_prob)
        
        latest_close = float(latest_data['Close'].values[0])
        latest_volume = int(latest_data['Volume'].values[0])
        
        history_df = df_features.tail(30)
        dates = history_df['Date'].dt.strftime('%Y-%m-%d').tolist()
        prices = history_df['Close'].tolist()
        volumes = history_df['Volume'].tolist()
        
        return {
            "ticker": ticker_symbol,
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": reasoning,
            "latest_price": latest_close,
            "latest_volume": latest_volume,
            "chart_data": {
                "dates": dates,
                "prices": prices,
                "volumes": volumes
            }
        }
        
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}

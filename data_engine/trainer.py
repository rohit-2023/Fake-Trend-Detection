import sys
sys.setrecursionlimit(50000)
import os
import yfinance as yf
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
from data_engine.features import calculate_features

def fetch_data(tickers, period="2y"):
    df_list = []
    for ticker in tickers:
        try:
            print(f"Fetching data for {ticker}...")
            data = yf.download(ticker, period=period, progress=False)
            if data.empty:
                continue
            
            # Formulate robust dataframe considering yfinance multiindex changes
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [c[0] for c in data.columns]
                
            data.reset_index(inplace=True)
            data['Ticker'] = ticker
            df_list.append(data)
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            
    if not df_list:
        return pd.DataFrame()
        
    return pd.concat(df_list, ignore_index=True)

def train_models():
    print("Starting Model Training Pipeline...")
    
    csv_path = os.path.join(os.path.dirname(__file__), 'nifty500_list.csv')
    if os.path.exists(csv_path):
        tickers = pd.read_csv(csv_path, header=None)[0].tolist()
    else:
        tickers = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS']
        
    print(f"Loaded {len(tickers)} tickers for training.")
    
    raw_data = fetch_data(tickers, period="2y")
    if raw_data.empty:
        raise ValueError("No data fetched. Check internet connection or tickers.")
        
    print(f"Raw data rows: {len(raw_data)}")
    
    processed_dfs = []
    for ticker in raw_data['Ticker'].unique():
        tdf = raw_data[raw_data['Ticker'] == ticker].copy()
        tdf = calculate_features(tdf, training=True)
        processed_dfs.append(tdf)
        
    final_df = pd.concat(processed_dfs, ignore_index=True)
    
    features = ['Price_Change', 'RSI', 'Volume_Spread', 'Wick_Ratio', 'TR', 'ATR']
    X = final_df[features]
    y = final_df['Is_Fake_Trend']
    
    print(f"Total samples for training: {len(X)}")
    print(f"Class counts before SMOTE:\n{y.value_counts()}")
    
    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X, y)
    print(f"Class counts after SMOTE:\n{pd.Series(y_resampled).value_counts()}")
    
    X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("Training XGBoost...")
    xgb_model = XGBClassifier(eval_metric='logloss', random_state=42)
    xgb_model.fit(X_train_scaled, y_train)
    print(f"XGBoost Accuracy: {xgb_model.score(X_test_scaled, y_test):.2f}")
    
    print("Training Random Forest...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train_scaled, y_train)
    print(f"Random Forest Accuracy: {rf_model.score(X_test_scaled, y_test):.2f}")
    
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    joblib.dump(xgb_model, os.path.join(models_dir, 'xgboost_model.pkl'))
    joblib.dump(rf_model, os.path.join(models_dir, 'rf_model.pkl'))
    joblib.dump(scaler, os.path.join(models_dir, 'scaler.pkl'))
    print(f"Models and Scaler saved successfully in {models_dir}!")

if __name__ == "__main__":
    train_models()

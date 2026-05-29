import pandas as pd
import numpy as np

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_features(df, training=False):
    """
    Calculates technical features for the DataFrame.
    DataFrame must contain: ['Open', 'High', 'Low', 'Close', 'Volume']
    """
    df = df.copy()
    
    # 1. Price Change (Daily Return)
    df['Price_Change'] = df['Close'].pct_change()
    
    # 2. RSI
    df['RSI'] = calculate_rsi(df)
    
    # 3. Volume-Price Divergence Feature
    df['Volume_MA_20'] = df['Volume'].rolling(window=20).mean()
    safe_ma = np.where(df['Volume_MA_20'] == 0, 1, df['Volume_MA_20'])
    df['Volume_Spread'] = np.where(df['Volume_MA_20'] == 0, 0, df['Volume'] / safe_ma)
    
    # 4. Candle Psychology: Wick Ratio
    num = df['High'] - df['Close']
    den = df['High'] - df['Low']
    safe_den = np.where(den == 0, 1, den)
    df['Wick_Ratio'] = np.where(den == 0, 0, num / safe_den)
    
    # Provide a simple True Range
    df['TR'] = np.maximum(
        df['High'] - df['Low'],
        np.maximum(
            abs(df['High'] - df['Close'].shift(1)),
            abs(df['Low'] - df['Close'].shift(1))
        )
    )
    df['ATR'] = df['TR'].rolling(window=14).mean()
    
    # Drop rows that don't have enough history for basic features
    feature_cols = ['Price_Change', 'RSI', 'Volume_Spread', 'Wick_Ratio', 'TR', 'ATR']
    df.dropna(subset=feature_cols, inplace=True)
    
    # 5. Labeling for Training: Fake Trend (Bull Trap)
    if training:
        df['Future_Return_3d'] = df['Close'].shift(-3) / df['Close'] - 1
        df['Is_Fake_Trend'] = np.where((df['Price_Change'] > 0) & (df['Future_Return_3d'] < -0.02), 1, 0)
        df.dropna(subset=['Future_Return_3d'], inplace=True)
        
    return df

# Smart Guard - Fake Trend Detection

Smart Guard is an AI-powered stock market analysis system designed to identify manipulated market movements, fake trends, bull traps, and liquidity grabs before they impact retail traders.

## Problem Statement

Traditional indicators such as RSI and Moving Averages often fail to detect institutional manipulation. This project uses machine learning to distinguish between sustainable trends and artificially created price movements.

## Features

* Fake Trend Detection
* Bull Trap Identification
* Volume-Price Divergence Analysis
* Wick (Candle Psychology) Analysis
* Sector Correlation Validation
* AI-Based Confidence Scoring

## Machine Learning Models

* XGBoost (Pattern Recognition)
* Isolation Forest (Anomaly Detection)
* SMOTE (Class Imbalance Handling)

## Tech Stack

* Python
* FastAPI
* XGBoost
* Isolation Forest
* yfinance
* backtesting.py

## Project Structure

* backend/
* frontend/
* data_engine/
* models/
* research_notebooks/

## Expected Output

The user enters a stock ticker (e.g., RELIANCE) and receives a prediction indicating whether the trend is REAL or FAKE, along with confidence scores and technical reasoning.

## Author

Rohit Kumar

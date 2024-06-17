# filename: stock_analysis.py

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

# Define the stock symbols
stocks = ['COST', 'CMG', 'TSLA', 'LLY']

# Define the time period (last 6 months)
end_date = datetime.now()
start_date = end_date - timedelta(days=6*30)

# Fetch the stock data
data = {}
for stock in stocks:
    data[stock] = yf.download(stock, start=start_date, end=end_date)

# Function to calculate moving average
def moving_average(data, window_size):
    return data.rolling(window=window_size).mean()

# Function to detect anomalies using z-score
def detect_anomalies(data, threshold=3):
    mean = np.mean(data)
    std = np.std(data)
    anomalies = data[(data - mean).abs() > threshold * std]
    return anomalies

# Plotting the data
fig, axs = plt.subplots(len(stocks), 1, figsize=(10, 20))

for i, stock in enumerate(stocks):
    stock_data = data[stock]['Close']
    ma = moving_average(stock_data, window_size=20)
    anomalies = detect_anomalies(stock_data)
    
    axs[i].plot(stock_data.index, stock_data, label='Stock Price')
    axs[i].plot(ma.index, ma, label='Moving Average (20 days)')
    axs[i].scatter(anomalies.index, anomalies, color='red', label='Anomalies')
    axs[i].set_title(f'{stock} Stock Price Analysis')
    axs[i].legend()

plt.tight_layout()
plt.show()
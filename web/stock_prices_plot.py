# filename: stock_prices_plot.py

import subprocess
import sys

# Function to install a package using pip
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Try to import yfinance, install if not available
try:
    import yfinance as yf
except ImportError:
    install("yfinance")
    import yfinance as yf

import matplotlib.pyplot as plt
import pandas as pd

# Define the stock tickers
tickers = ['COST', 'CMG', 'TSLA', 'LLY']

# Fetch the stock data for the year-to-date (YTD)
data = yf.download(tickers, start="2023-01-01", end=pd.Timestamp.today().strftime('%Y-%m-%d'))

# Extract the opening and closing prices
open_prices = data['Open']
close_prices = data['Close']

# Plot the data
plt.figure(figsize=(14, 7))

# Plot opening prices
for ticker in tickers:
    plt.plot(open_prices.index, open_prices[ticker], label=f'{ticker} Open')

# Plot closing prices
for ticker in tickers:
    plt.plot(close_prices.index, close_prices[ticker], linestyle='--', label=f'{ticker} Close')

plt.title('YTD Stock Prices for Costco, Chipotle, Tesla, and Eli Lilly')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.legend()
plt.grid(True)
plt.show()
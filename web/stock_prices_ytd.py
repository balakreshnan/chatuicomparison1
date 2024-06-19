# filename: stock_prices_ytd.py

import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# Define the stock symbols
stocks = ['COST', 'CMG', 'TSLA', 'LLY']

# Fetch the stock data YTD
data = yf.download(stocks, start='2023-01-01', end=pd.Timestamp.today().strftime('%Y-%m-%d'))

# Extract the opening and closing prices
open_prices = data['Open']
close_prices = data['Close']

# Plot the opening prices
plt.figure(figsize=(14, 7))
for stock in stocks:
    plt.plot(open_prices.index, open_prices[stock], label=f'{stock} Open')

plt.title('Opening Prices YTD')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.grid(True)
plt.show()

# Plot the closing prices
plt.figure(figsize=(14, 7))
for stock in stocks:
    plt.plot(close_prices.index, close_prices[stock], label=f'{stock} Close')

plt.title('Closing Prices YTD')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.grid(True)
plt.show()
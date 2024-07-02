# filename: stock_prices_plot.py

import yfinance as yf
import matplotlib.pyplot as plt
import datetime

# Define the stock tickers
tickers = ['COST', 'CMG', 'TSLA', 'LLY']

# Get the current date
end_date = datetime.datetime.now().strftime('%Y-%m-%d')

# Get the start date for YTD
start_date = f"{datetime.datetime.now().year}-01-01"

# Download stock data
data = yf.download(tickers, start=start_date, end=end_date)

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
    plt.plot(close_prices.index, close_prices[ticker], label=f'{ticker} Close', linestyle='--')

plt.title('YTD Stock Prices for Costco, Chipotle, Tesla, and Eli Lilly')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.legend()
plt.grid(True)
plt.show()
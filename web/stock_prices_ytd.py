# filename: stock_prices_ytd.py

import yfinance as yf
import matplotlib.pyplot as plt
import datetime

# Define the stock tickers
tickers = {
    'Costco': 'COST',
    'Chipotle': 'CMG',
    'Tesla': 'TSLA',
    'Eli Lilly': 'LLY'
}

# Get the current date and the start of the year
end_date = datetime.datetime.now()
start_date = datetime.datetime(end_date.year, 1, 1)

# Fetch the stock data
data = {}
for company, ticker in tickers.items():
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    data[company] = stock_data

# Plot the data
plt.figure(figsize=(14, 7))

for company, stock_data in data.items():
    plt.plot(stock_data.index, stock_data['Open'], label=f'{company} Open')
    plt.plot(stock_data.index, stock_data['Close'], label=f'{company} Close')

plt.title('Stock Prices YTD (Opening and Closing)')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save the plot as an image file
plt.savefig('stock_prices_ytd.png')

# Show the plot
plt.show()
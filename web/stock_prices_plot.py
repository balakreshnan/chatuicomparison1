# filename: stock_prices_plot.py

import yfinance as yf
import matplotlib.pyplot as plt
import datetime

# Define the stock symbols
stocks = {
    'Costco': 'COST',
    'Chipotle': 'CMG',
    'Tesla': 'TSLA',
    'Eli Lilly': 'LLY'
}

# Get the current date and the start of the year
end_date = datetime.datetime.now()
start_date = datetime.datetime(end_date.year, 1, 1)

# Fetch the stock data
stock_data = {}
for company, symbol in stocks.items():
    stock_data[company] = yf.download(symbol, start=start_date, end=end_date)

# Plot the stock data
plt.figure(figsize=(14, 7))

for company, data in stock_data.items():
    plt.plot(data['Close'], label=company)

plt.title('YTD Stock Prices')
plt.xlabel('Date')
plt.ylabel('Closing Price (USD)')
plt.legend()
plt.grid(True)
plt.show()
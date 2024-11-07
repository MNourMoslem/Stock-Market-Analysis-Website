import plotly.graph_objects as go
import pandas as pd
import yfinance as yf

# Fetch stock data using yfinance
stock_data = yf.download('AAPL', start='2023-01-01', end='2024-01-01')

# Create a candlestick chart
fig = go.Figure(data=[go.Candlestick(
    x=stock_data.index,
    open=stock_data['Open'],
    high=stock_data['High'],
    low=stock_data['Low'],
    close=stock_data['Close'],
    name='AAPL Stock Price'
)])

# Add title and labels
fig.update_layout(
    title="AAPL Stock Price (2023-2024)",
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    xaxis_rangeslider_visible=False
)

# Show the plot (this can be saved as an HTML file or displayed in a Jupyter notebook)
fig.write_html("stock_graph.html")


import pandas as pd

hist = pd.read_csv('./5k_history.csv')
info = pd.read_csv('./5k_info.csv')

info.to_sql('./Tickers.db')
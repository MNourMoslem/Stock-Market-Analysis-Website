import pandas as pd
import requests
import yfinance as yf
from typing import List

N = 300

tickers : List[yf.Ticker] = [None] * N

with open("./5k_tickers.csv", 'r') as file:
    print("Data Tickers being prepared:")
    for i in range(len(tickers)):
        ticker_name = file.readline().strip()
        tickers[i] = yf.Ticker(ticker_name)
        print(f"{i+1} / {N} is completed", end='\r')
print('')
print('')

start_date = "2024-10-06"
period = "1mo"

stock_info = pd.DataFrame(columns=['id', 'Symbol', 'Industry', 'Country', 'Brand', "Sector"])
stock_history = pd.DataFrame()

dicard_count = 0
id = 1

print("Collecting Data:")
for i, ticker in enumerate(tickers[:N]):
    info = ticker.info

    if 'symbol' not in info:
        dicard_count += 1
        continue

    hist = ticker.history(period = period).reset_index()
    hist['id'] = id

    industry, country = info.get('industry', None) ,info.get('country', None)
    brand, sector = info.get('longName', None), info.get('sector')
    symbol = info['symbol']

    if industry and country:
        stock_info.loc[len(stock_info.index)] = [id, symbol, industry,  country, brand, sector] 
    else:
        dicard_count += 1
        continue

    try:
        shares = ticker.get_shares_full(start = start_date, end = None)
    except:
        dicard_count += 1
        continue

    if not isinstance(shares, type(None)):
        shares = shares.reset_index()
        hist = pd.merge(hist, shares, how='left', left_on='Date', right_on='index')
        hist = hist.rename(columns={0 : 'Shares Outstanding'})
        hist['Shares Outstanding'] = hist['Shares Outstanding'].bfill()
    else:
        dicard_count += 1
        continue

    hist['Market Capital'] = hist['Close'] * hist['Shares Outstanding']
    
    stock_history = pd.concat((stock_history, hist))

    id += 1

    print(f"{i+1} / {N} is completed, {dicard_count} discarded", end='\r')

    if ((i % 100) == 0):
        stock_history.to_csv('./5k_history.csv')
        stock_info.to_csv('./5k_info.csv')

print('')
print(f'{dicard_count} has been removed due non exicting in the database on yfinance')
print('')

stock_history = stock_history.drop(columns=['index'])
stock_history = stock_history.drop_duplicates(subset = ['Symbol' ,'Date'], keep='last')
stock_history = stock_history.reset_index(drop = True)

stock_history.to_csv('./5k_history.csv')
stock_info.to_csv('./5k_info.csv')

print(stock_history)
print(stock_info)

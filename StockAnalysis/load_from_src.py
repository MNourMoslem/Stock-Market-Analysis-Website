import pandas as pd
import requests
import yfinance as yf
from typing import List

def load_history_from_src(symbols : List[str], stock_ids : List[int], start_date : str, period : str, out_path_prefix : str = "temp"):
    tickers : List[yf.Ticker] = [None] * len(symbols)

    for i, symbol in enumerate(symbols):
        tickers[i] = yf.Ticker(symbol.strip())
    stock_history = pd.DataFrame()

    dicard_count = 0
    print("Collecting Data:")
    for i, ticker in enumerate(tickers):
        info = ticker.info

        if 'symbol' not in info:
            dicard_count += 1
            continue

        hist = ticker.history(period = period).reset_index()
        hist['id'] = stock_ids[i]

        industry = info.get('industry', None)
        country = info.get('country', None)
        brand = info.get('longName', None)
        sector = info.get('sector', None)
        symbol = info.get('symbol', None)

        if not (symbol and sector and industry and country and brand):
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
            hist['Shares Outstanding'] = hist['Shares Outstanding'].bfill().ffill()
        else:
            dicard_count += 1
            continue

        hist['Market Capital'] = hist['Close'] * hist['Shares Outstanding']
        
        stock_history = pd.concat((stock_history, hist))

        print(f"{i+1} / {len(symbols)} is completed, {dicard_count} discarded", end='\r')
    print(f'\n{dicard_count} has been removed due non exicting in the database of yfinance\n')

    stock_history = stock_history.drop(columns=['index'])
    stock_history = stock_history.drop_duplicates(subset = ['id', 'Date'], keep='last')
    stock_history = stock_history.reset_index(drop = True)

    stock_history.to_csv(f'{out_path_prefix}_stock_history.csv')
import pandas as pd
import requests
import yfinance as yf
from typing import List

N = 400
prefix = "temp"

tickers : List[yf.Ticker] = [None] * N

with open("./5k_tickers.csv", 'r') as file:
    print("Data Tickers being prepared:")
    for i in range(len(tickers)):
        ticker_name = file.readline().strip()
        tickers[i] = yf.Ticker(ticker_name)
        print(f"{i+1} / {N} is completed", end='\r')
    print('\n')

start_date = "2000-01-01"
period = "max"

stock_info = pd.DataFrame(columns=['id', 'Symbol', 'Industry_Id', 'Country_Id', 'Brand'])
stock_history = pd.DataFrame()
industry_dict = {}
ind2sec_dict = {}
sector_dict = {}
country_dict = {}

dicard_count = 0
id = 1

sector_id = 1
industry_id = 1
country_id = 1

print("Collecting Data:")
for i, ticker in enumerate(tickers[:N]):
    try:
        info = ticker.info
    except:
        dicard_count += 1
        continue

    if 'symbol' not in info:
        dicard_count += 1
        continue

    hist = ticker.history(period = period).reset_index()
    hist['id'] = id

    industry = info.get('industry', None)
    country = info.get('country', None)
    brand = info.get('longName', None)
    sector = info.get('sector', None)
    symbol = info.get('symbol', None)

    if not (symbol and sector and industry and country and brand):
        dicard_count += 1
        continue

    if sector not in sector_dict:
        sector_dict[sector] = sector_id
        sector_id += 1

    if industry not in industry_dict:
        industry_dict[industry] = industry_id
        ind2sec_dict[industry_id] = sector_dict[sector]
        industry_id += 1

    if country not in country_dict:
        country_dict[country] = country_id
        country_id += 1

    stock_info.loc[len(stock_info.index)] = [id, symbol, industry_dict[industry], country_dict[country], brand] 

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

    id += 1

    print(f"{i+1} / {N} is completed, {dicard_count} discarded", end='\r')
print(f'\n{dicard_count} has been removed due non exicting in the database of yfinance\n')

stock_history = stock_history.drop(columns=['index'])
stock_history = stock_history.drop_duplicates(subset = ['id', 'Date'], keep='last')
stock_history = stock_history.reset_index(drop = True)

industry_df = pd.DataFrame({"name" : industry_dict.keys(), "sector_id" : ind2sec_dict.values()}, index=industry_dict.values())
sector_df = pd.DataFrame(sector_dict.keys(), index=sector_dict.values(), columns=['name'])
country_df = pd.DataFrame(country_dict.keys(), index=country_dict.values(), columns=['name'])

stock_history.to_csv(f'{prefix}_stock_history.csv')
stock_info.to_csv(f'{prefix}_stock_info.csv')
industry_df.to_csv(f"{prefix}_stock_industry.csv", index_label='id')
sector_df.to_csv(f"{prefix}_stock_sector.csv", index_label='id')
country_df.to_csv(f"{prefix}_stock_country.csv", index_label='id')

print(stock_history)
print(stock_info)
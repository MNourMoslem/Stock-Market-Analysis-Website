import os
import django
import csv
from datetime import datetime
from django.db import transaction
from django.utils.timezone import make_aware, localtime
import inspect
import sqlite3

import pandas as pd

from load_from_src import load_history_from_src

def myfunc():
    print(f"Currently working in {inspect.currentframe().f_code.co_name}")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockAnalysis.settings')  
django.setup()

from stock.models import History, Stock, Industry, Country, Sector


DATA_DIR = os.getcwd()

prefix = "mini"

def read_country(path):
    func_name = inspect.currentframe().f_code.co_name
    with open(path) as countryFile:
        cntrys = csv.DictReader(countryFile)
        with transaction.atomic():
            for i, info in enumerate(cntrys, start = 1):
                print(f"Working on {func_name}, {i} completed.", end='\r')
                name = info['name']
                id = info['id']

                Country.objects.create(id = id, name = name)
    print(f"\n{func_name} is Done")

def read_sector(path):
    func_name = inspect.currentframe().f_code.co_name
    with open(path) as sectorFile:
        sctrs = csv.DictReader(sectorFile)
        with transaction.atomic():
            for i, info in enumerate(sctrs, start = 1):
                print(f"Working on {func_name}, {i} completed.", end='\r')
                name = info['name']
                id = info['id']
                
                Sector.objects.create(id = id, name = name)
    print(f"\n{func_name} is Done")

def read_industry(path):
    func_name = inspect.currentframe().f_code.co_name
    with open(path) as industryFile:
        inds = csv.DictReader(industryFile)
        with transaction.atomic():
            for i, info in enumerate(inds, start = 1):
                print(f"Working on {func_name}, {i} completed.", end='\r')
                name = info['name']
                id = info['id']
                sector_id = info['sector_id']
                sector = Sector.objects.get(id = sector_id)
                Industry.objects.create(id = id, name = name, sector = sector)

    print(f"\n{func_name} is Done")

def read_info(path):
    func_name = inspect.currentframe().f_code.co_name
    with open(path) as infoFile:
        inf = csv.DictReader(infoFile)
        with transaction.atomic():
            for i, info in enumerate(inf, start = 1):
                print(f"Working on {func_name}, {i} completed.", end='\r')
                id = info['id']
                country = Country.objects.get(id = info["Country_Id"])
                brand = info['Brand']
                industry = Industry.objects.get(id = info["Industry_Id"])
                symbol = info['Symbol']

                Stock.objects.create(
                    id = id,
                    brand = brand,
                    industry = industry,
                    country = country,
                    symbol = symbol
                )
    print(f"\n{func_name} is Done")

def read_history(path):
    func_name = inspect.currentframe().f_code.co_name
    hist_df = pd.read_csv(path, parse_dates=['Date']).drop(columns=["Unnamed: 0"])
    hist_df['Date'] = pd.to_datetime(hist_df['Date'], utc=True)
    sqlite_db_path = "./db.sqlite3"

    new_column_names = [
        'date', 
        'open_price', 
        'high_price', 
        'low_price', 
        'close_price', 
        'volume', 
        'dividends', 
        'stock_splits', 
        'stock_id',
        'shares_outstanding', 
        'market_cap'
    ]

    if "Adj Close" in hist_df.columns:
        hist_df.drop(columns=["Adj Close"], inplace=True)

    print(hist_df.columns)
    hist_df.columns = new_column_names

    print(f"Working on {func_name}...")

    conn = sqlite3.connect(sqlite_db_path)
    hist_df.to_sql('stock_history', conn, if_exists='append', index=False)
    conn.close()

    print(f"\n{func_name} is Done")

def recover_info(from_date : str):
    print("Recoverin info...")
    stocks = Stock.objects.all()
    for stock in stocks:
        stock.update_stock_from_history(from_date)

def load_history_from_src_and_update_db(prefix : str = 'temp'):
    symbols = list(Stock.objects.all().values_list('symbol', flat=True))
    last_date = History.objects.all().order_by('-date').first().date
    
    load_history_from_src(symbols, last_date, "max", prefix)

    HISTORY_FILE_PATH = os.path.join(DATA_DIR, f"{prefix}_stock_history.csv")

    read_history(HISTORY_FILE_PATH)
    recover_info(last_date)

    os.remove(HISTORY_FILE_PATH)
    print("Done!")

def load_data():
    DATA_DIR = os.path.join(os.getcwd(), "../data")
    prefix = "temp"

    COUNTRY_FILE_PATH = os.path.join(DATA_DIR, f"{prefix}_stock_country.csv")
    SECTOR_FILE_PATH = os.path.join(DATA_DIR, f"{prefix}_stock_sector.csv")
    INDUSTRY_FILE_PATH = os.path.join(DATA_DIR, f"{prefix}_stock_industry.csv")
    INFO_FILE_PATH = os.path.join(DATA_DIR, f"{prefix}_stock_info.csv")
    HISTORY_FILE_PATH = os.path.join(DATA_DIR, f"{prefix}_stock_history.csv")

    read_country(COUNTRY_FILE_PATH)
    read_sector(SECTOR_FILE_PATH)
    read_industry(INDUSTRY_FILE_PATH)
    read_info(INFO_FILE_PATH)
    read_history(HISTORY_FILE_PATH)
    recover_info(None)
    print("Done!")

if __name__ == "__main__":
    load_data()

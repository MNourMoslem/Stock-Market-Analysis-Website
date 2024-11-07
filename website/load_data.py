import os
import django
import csv
from datetime import datetime
from django.db import transaction
from django.utils.timezone import make_aware, localtime

# Set the default settings module for the Django project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_market_website.settings')  # Replace 'website.settings' with your project name
django.setup()

from stock.models import History, Stock  # Now you can import models after setting up Django

# File paths
HISTORY_FILE_PATH = r"C:\Users\Abed\Desktop\Stock Market Analysis Project\data\5k_history.csv"
INFO_FILE_PATH = r"C:\Users\Abed\Desktop\Stock Market Analysis Project\data\5k_info.csv"

def load_data():
    with open(INFO_FILE_PATH, newline='') as infoFile:
        info = csv.DictReader(infoFile)
        with transaction.atomic():  # Ensure atomicity for database operations
            for row in info:
                sector = row['Sector'] if row['Sector'] else None
                contry = row['Country'] if row['Country'] else None
                brand = row['Brand'] if row['Brand'] else None
                industry = row['Industry'] if row['Industry'] else None
                symbol = row['Symbol'] if row['Symbol'] else None

                # Create Stock record if it doesn't exist
                stock, created = Stock.objects.get_or_create(
                    symbol=symbol,
                    defaults={
                        'sector': sector,
                        'brand': brand,
                        'industry': industry,
                        'country': contry
                    }
                )

                # After creating the stock, update its price and market cap from the latest History
                stock.update_stock_from_history()

    with open(HISTORY_FILE_PATH, newline='') as histFile:
        hist = csv.DictReader(histFile)
        
        with transaction.atomic():  # Ensure atomicity for database operations
            for i, row in enumerate(hist):
                print(i)
                # Parse history data
                id = int(float(row['id'])) if row['id'] else None
                date = datetime.strptime(row['Date'], '%Y-%m-%d %H:%M:%S%z')  # Keep time zone info
                open_price = float(row['Open']) if row['Open'] else None
                high_price = float(row['High']) if row['High'] else None
                low_price = float(row['Low']) if row['Low'] else None
                close_price = float(row['Close']) if row['Close'] else None
                volume = int(float(row['Volume'])) if row['Volume'] else None
                dividends = float(row['Dividends']) if row['Dividends'] else None
                stock_splits = float(row['Stock Splits']) if row['Stock Splits'] else None
                shares_outstanding = int(float(row['Shares Outstanding'])) if row['Shares Outstanding'] else 0
                market_cap = float(row['Market Capital']) if row['Market Capital'] else 0.0

                stock = Stock.objects.get(id=id)

                History.objects.create(
                    stock=stock,
                    date=localtime(date),  # Make datetime timezone-aware
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    volume=volume,
                    dividends=dividends,
                    stock_splits=stock_splits,
                    shares_outstanding=shares_outstanding,
                    market_cap=market_cap
                )


if __name__ == "__main__":
    load_data()

from django.shortcuts import render
from stock.models import Stock

def table_view(request):
    stocks = Stock.objects.all().order_by('symbol')

    table_columns = ["Symbol", "Brand", "Price", "Market Cap"]

    table_data = [
        (stock, [stock.symbol, stock.brand, stock.price, stock.market_cap])
        for stock in stocks
    ]

    context = {
        "table_columns": table_columns,
        "table_data": table_data,
        "n_stocks": len(table_data),
    }

    return render(request, "table/stock_table.html", context)

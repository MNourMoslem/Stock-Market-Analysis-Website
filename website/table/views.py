from django.shortcuts import render
from stock.models import Stock

def table_view(request):
    # Retrieve stocks from the database and order them alphabetically by 'symbol'
    stocks = Stock.objects.all().order_by('symbol')

    # Define the columns you want to display in the table
    table_columns = ["Symbol", "Brand", "Price", "Market Cap"]

    # Format the rows for the table with the stock ID in a separate list
    table_data = [
        (stock, [stock.symbol, stock.brand, stock.price, stock.market_cap])
        for stock in stocks
    ]

    # Context for rendering the table
    context = {
        "table_columns": table_columns,
        "table_data": table_data,  # Now each entry has the stock_id and row data
        "n_stocks": len(table_data),
    }

    return render(request, "table/stock_table.html", context)

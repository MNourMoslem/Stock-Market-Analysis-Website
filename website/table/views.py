from django.shortcuts import render
from stock.models import *

def _get_table(stocks):
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

    return context

def table_view(request):
    stocks = Stock.objects.all().order_by('symbol')
    context = _get_table(stocks)
    return render(request, "table/stock_table.html", context)

def by_industry_view(request):
    sctrs = Sector.objects.all()
    sctrs = [
        (sector.name, Industry.objects.filter(sector_id = sector.id)) for sector in sctrs
    ]

    context = {
        "sectors" : sctrs
    }

    return render(request, "table/by_industry.html", context)

def industry_table_view(request, industry_id):
    stks = Stock.objects.filter(industry_id = industry_id)
    context =  _get_table(stks)
    context['industry_name'] = Industry.objects.get(id = industry_id).name
    return render(request, "table/industry_table.html", context)
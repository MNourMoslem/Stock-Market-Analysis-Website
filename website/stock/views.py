from django.shortcuts import render, get_object_or_404
from stock.models import Stock, History  # Import History model as well
from django.db.models import Max

def stock_card_view(request, stock_symbol):
    stock = Stock.objects.get(symbol=stock_symbol)

    latest_history = History.objects.filter(stock=stock).order_by('-date').first()

    if not latest_history:
        context = {
            'stock_symbol': stock.symbol,
            'error': 'No transaction history available for this stock.',
        }
        return render(request, 'stock_card.html', context)

    context = {
        'stock_symbol': stock.symbol,
        'stock_close': latest_history.close_price,
        'stock_open': latest_history.open_price,
        'stock_high': latest_history.high_price,
        'stock_low': latest_history.low_price,
        'stock_volume': latest_history.volume,
    }

    return render(request, 'stock/stock_card.html', context)

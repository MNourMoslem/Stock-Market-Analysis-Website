from django.shortcuts import render, get_object_or_404
from stock.models import Stock, History  # Import History model as well
from django.db.models import Max

def stock_card_view(request, stock_symbol):
    # Retrieve the specific stock by ID
    stock = Stock.objects.get(symbol=stock_symbol)

    # Get the latest transaction record for this stock
    latest_history = History.objects.filter(stock=stock).order_by('-date').first()

    if not latest_history:
        # Handle case if no history records are found
        context = {
            'stock_symbol': stock.symbol,
            'error': 'No transaction history available for this stock.',
        }
        return render(request, 'stock_card.html', context)

    # Prepare the stock details from the latest history
    stock_data = {
        'labels': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],  # Example labels
        'datasets': [
            {
                'label': f'{stock.symbol} (USD)',
                'data': [150, 155, 160, 158, 162],  # Sample data; replace with actual historical data if available
                'borderColor': 'rgba(75, 192, 192, 1)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'fill': True
            }
        ]
    }

    # Chart configuration
    chart_config = {
        'type': 'line',
        'options': {
            'responsive': True,
            'scales': {
                'x': {
                    'title': {'display': True, 'text': 'Date'}
                },
                'y': {
                    'title': {'display': True, 'text': 'Price (USD)'}
                }
            }
        }
    }

    # Context for rendering the template
    context = {
        'stock_symbol': stock.symbol,
        'stock_close': latest_history.close_price,
        'stock_open': latest_history.open_price,
        'stock_high': latest_history.high_price,
        'stock_low': latest_history.low_price,
        'stock_volume': latest_history.volume,
        'stock_data': stock_data,
        'chart_config': chart_config
    }

    return render(request, 'stock/stock_card.html', context)

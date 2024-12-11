from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from .models import Stock, Sector, Industry, Country, History
from django.http import JsonResponse
import json
from datetime import datetime, timedelta

def stock_list(request):
    # جلب جميع الأسهم من قاعدة البيانات مرتبة حسب الرمز
    stocks_queryset = Stock.objects.all().select_related(
        'industry', 
        'industry__sector', 
        'country'
    ).order_by('symbol')  # تغيير الترتيب من brand إلى symbol
    
    # تحديد الأعمدة التي نريد عرضها
    columns = ['Brand', 'Price', 'Sector', 'Industry', 'Country']
    
    # تحويل البيانات إلى التنسيق المطلوب للقالب
    stocks = [
        {
            'symbol': stock.symbol,
            'fields': [
                stock.brand,
                f'${stock.price:.2f}',
                stock.industry.sector.name if stock.industry and stock.industry.sector else '-',
                stock.industry.name if stock.industry else '-',
                stock.country.name if stock.country else '-'
            ]
        }
        for stock in stocks_queryset
    ]
    
    context = {
        'columns': columns,
        'stocks': stocks
    }
    return render(request, 'stock/stocks.html', context)

def stock_detail(request, symbol):
    stock = get_object_or_404(Stock, symbol=symbol)
    last_history = stock.history_entries.order_by('-date').first()
    
    context = {
        'stock': stock,
        'last_history': last_history,
    }
    return render(request, 'stock/stock_detail.html', context)

def by_industry(request):
    # جلب القطاعات مع الصناعات المرتبطة وعدد الأسهم لكل صناعة
    sectors = Sector.objects.prefetch_related('industry_sector').all()
    
    sectors_data = []
    for sector in sectors:
        industries = sector.industry_sector.annotate(
            stock_count=Count('stock_industry')
        ).order_by('name')
        
        sectors_data.append({
            'name': sector.name,
            'industries': industries
        })
    
    return render(request, 'stock/by_industry.html', {'sectors': sectors_data})

def industry_stocks(request, industry_id):
    # جلب الصناعة المحددة
    industry = get_object_or_404(Industry, id=industry_id)
    
    # جلب الأسهم المرتبطة بهذه الصناعة
    stocks_queryset = Stock.objects.filter(
        industry=industry
    ).select_related(
        'industry', 
        'industry__sector', 
        'country'
    ).order_by('symbol')
    
    columns = ['Brand', 'Price', 'Sector', 'Industry', 'Country']
    
    stocks = [
        {
            'symbol': stock.symbol,
            'fields': [
                stock.brand,
                f'${stock.price:.2f}',
                stock.industry.sector.name if stock.industry and stock.industry.sector else '-',
                stock.industry.name if stock.industry else '-',
                stock.country.name if stock.country else '-'
            ]
        }
        for stock in stocks_queryset
    ]
    
    context = {
        'columns': columns,
        'stocks': stocks,
        'industry_name': industry.name
    }
    return render(request, 'stock/stocks.html', context)

def by_country(request):
    # جلب الدول مع عدد الأسهم لكل دولة
    countries = Country.objects.annotate(
        stock_count=Count('stock_country')
    ).order_by('name')
    
    return render(request, 'stock/by_country.html', {'countries': countries})

def country_stocks(request, country_id):
    # جلب الدولة المحددة
    country = get_object_or_404(Country, id=country_id)
    
    # جلب الأسهم المرتبطة بهذه الدولة
    stocks_queryset = Stock.objects.filter(
        country=country
    ).select_related(
        'industry', 
        'industry__sector', 
        'country'
    ).order_by('symbol')
    
    columns = ['Brand', 'Price', 'Sector', 'Industry', 'Country']
    
    stocks = [
        {
            'symbol': stock.symbol,
            'fields': [
                stock.brand,
                f'${stock.price:.2f}',
                stock.industry.sector.name if stock.industry and stock.industry.sector else '-',
                stock.industry.name if stock.industry else '-',
                stock.country.name if stock.country else '-'
            ]
        }
        for stock in stocks_queryset
    ]
    
    context = {
        'columns': columns,
        'stocks': stocks,
        'country_name': country.name
    }
    return render(request, 'stock/stocks.html', context)

def search_stocks(request):
    query = request.GET.get('query', '').strip()
    
    if len(query) < 1:
        return JsonResponse({'results': []})
    
    # البحث عن الأسهم التي تبدأ بالحروف المدخلة
    stocks = Stock.objects.filter(
        symbol__istartswith=query
    ).select_related('industry', 'country').order_by('symbol')[:10]
    
    results = [{
        'symbol': stock.symbol,
        'brand': stock.brand,
        'price': f"${stock.price:.2f}",
        'country': stock.country.name if stock.country else '-',
        'url': f"/stock/{stock.symbol}/"
    } for stock in stocks]
    
    return JsonResponse({'results': results})

def home(request):
    return render(request, 'stock/home.html')

def get_stock_history(request):
    symbol = request.GET.get('symbol')
    time_range = request.GET.get('range', '1M')
    metric = request.GET.get('metric', 'close_price')
    
    if not symbol:
        return JsonResponse({'error': 'Symbol is required'}, status=400)
    
    end_date = datetime.now()
    if time_range == '1M':
        start_date = end_date - timedelta(days=30)
    elif time_range == '3M':
        start_date = end_date - timedelta(days=90)
    elif time_range == '6M':
        start_date = end_date - timedelta(days=180)
    elif time_range == '1Y':
        start_date = end_date - timedelta(days=365)
    else:  # 5Y
        start_date = end_date - timedelta(days=1825)
    
    history = History.objects.filter(
        stock__symbol=symbol,
        date__range=(start_date, end_date)
    ).order_by('date')
    
    dates = [entry.date.strftime('%Y-%m-%d') for entry in history]
    data = {
        'dates': dates,
        'prices': [float(entry.close_price) for entry in history],
        'volume': [entry.volume for entry in history],
        'market_cap': [float(entry.market_cap) if entry.market_cap else None for entry in history],
        'shares_outstanding': [entry.shares_outstanding for entry in history]
    }
    
    return JsonResponse(data)

def compare(request):
    # Define available metrics with their display names and field types
    available_metrics = {
        'close_price': {'label': 'Close Price', 'type': 'price'},
        'open_price': {'label': 'Open Price', 'type': 'price'},
        'high_price': {'label': 'High Price', 'type': 'price'},
        'low_price': {'label': 'Low Price', 'type': 'price'},
        'volume': {'label': 'Volume', 'type': 'number'},
        'dividends': {'label': 'Dividends', 'type': 'price'},
        'stock_splits': {'label': 'Stock Splits', 'type': 'number'},
        'shares_outstanding': {'label': 'Shares Outstanding', 'type': 'number'},
        'market_cap': {'label': 'Market Cap', 'type': 'price'}
    }

    # Define table columns with their data mappings
    table_columns = {
        'Brand': {'field': 'brand'},
        'Industry': {'field': 'industry', 'nested': True},
        'Sector': {'field': 'sector', 'nested': True},
        'Country': {'field': 'country', 'nested': True}
    }

    return render(request, 'stock/compare.html', {
        'title': 'Compare Stocks',
        'columns': table_columns,
        'stocks': list(),  # Pass an empty list instead of []
        'metrics': available_metrics
    })

def get_stock_details(request):
    symbol = request.GET.get('symbol')
    if not symbol:
        return JsonResponse({'error': 'Symbol is required'}, status=400)
    
    try:
        stock = Stock.objects.select_related('industry__sector', 'country').get(symbol=symbol)
        return JsonResponse({
            'symbol': stock.symbol,
            'brand': stock.brand,
            'industry': stock.industry.name if stock.industry else None,
            'sector': stock.industry.sector.name if stock.industry and stock.industry.sector else None,
            'country': stock.country.name if stock.country else None,
        })
    except Stock.DoesNotExist:
        return JsonResponse({'error': 'Stock not found'}, status=404)
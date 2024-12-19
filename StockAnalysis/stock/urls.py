from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('stocks/', views.stock_list, name='stock_list'),
    path('stock/<str:symbol>/', views.stock_detail, name='stock_detail'),
    path('by-industry/', views.by_industry, name='by_industry'),
    path('industry/<int:industry_id>/', views.industry_stocks, name='industry_stocks'),
    path('by-country/', views.by_country, name='by_country'),
    path('country/<int:country_id>/', views.country_stocks, name='country_stocks'),
    path('api/search/', views.search_stocks, name='search_stocks'),
    path('api/stock-history/', views.get_stock_history, name='stock_history'),
    path('compare/', views.compare, name='compare'),
    path('api/stock-details/', views.get_stock_details, name='stock_details'),
    path('api/update-stocks/', views.update_stocks, name='update_stocks'),
]

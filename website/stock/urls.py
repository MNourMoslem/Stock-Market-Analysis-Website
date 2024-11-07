from django.urls import path
from .views import stock_card_view

urlpatterns = [
    path('stock/<str:stock_symbol>/', stock_card_view, name='stock_card'),
]

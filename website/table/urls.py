from django.urls import path
from .views import *

urlpatterns = [
    path('table/', table_view, name='stock_table'),
    path('by_industry/', by_industry_view, name='by_industry_list'),
    path('by_industry/<int:industry_id>', industry_table_view, name='industry_table'),
]

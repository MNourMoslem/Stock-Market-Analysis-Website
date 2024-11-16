from django.contrib import admin
from django.urls import path, include
import table.urls
import home.urls
import stock.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('table/', include(table.urls)),
    path('stock_card/', include(stock.urls)),
    path('home/', include(home.urls))
]

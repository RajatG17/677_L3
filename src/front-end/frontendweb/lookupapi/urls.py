from django.urls import path
from . import views

urlpatterns = [
    path('stocks/<str:stockname>', views.getstocks, name='getstocks'),
    path('orders/<int:ordernumber>', views.getorders, name='getorders'),
    path('orders/', views.postorders, name='postorders'),
    path('stocksCache/<str:stockname>', views.getstocksCache, name='getstocksCache'),
]

from django.urls import path
from .views import Home, Product, HomeWomen

urlpatterns = [
    path('', Home.as_view(), name = 'home'),
    path('main/', Home.as_view(), name = 'home'),
    path('main/women/', HomeWomen.as_view(), name = 'home_women'),
    path('main/products/', Product.as_view(), name = 'products'),
]
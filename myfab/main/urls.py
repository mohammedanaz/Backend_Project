from django.urls import path
from .views import Home, Product

urlpatterns = [
    path('', Home.as_view(), name = 'home'),
    path('main/', Home.as_view(), name = 'home'),
    path('main/products/', Product.as_view(), name = 'products'),
]
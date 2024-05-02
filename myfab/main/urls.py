from django.urls import path
from .views import Home, ProductPage, HomeWomen

urlpatterns = [
    path('', Home.as_view(), name = 'home'),
    path('main/', Home.as_view(), name = 'home'),
    path('main/women/', HomeWomen.as_view(), name = 'home_women'),
    path('main/products/', ProductPage.as_view(), name = 'products'),
]
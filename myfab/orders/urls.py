from django.urls import path
from .views import CartView, CheckoutView


urlpatterns = [
   path('cart/', CartView.as_view(), name = 'cart'),
   path('checkout/', CheckoutView.as_view(), name = 'checkout'),
]
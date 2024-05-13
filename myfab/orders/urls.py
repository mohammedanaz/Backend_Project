from django.urls import path
from .views import CartView, CheckoutView, CreateOrder


urlpatterns = [
   path('cart/', CartView.as_view(), name = 'cart'),
   path('checkout/', CheckoutView.as_view(), name = 'checkout'),
   path('create_order/', CreateOrder.as_view(), name = 'create_order'),
]
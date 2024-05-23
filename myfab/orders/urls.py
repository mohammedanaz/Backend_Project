from django.urls import path
from .views import CartView, CheckoutView, CreateOrder, CartDelete, CartEdit
from .views import Invoice, PaymentCallback
from . import views


urlpatterns = [
   path('cart/', CartView.as_view(), name = 'cart'),
   path('checkout/', CheckoutView.as_view(), name = 'checkout'),
   path('create_order/', CreateOrder.as_view(), name = 'create_order'),
   path('payment_callback/', PaymentCallback.as_view(), name = 'payment_callback'),
   path('delete_cart/', CartDelete.as_view(), name = 'delete_cart'),
   path('edit_cart/', CartEdit.as_view(), name = 'edit_cart'),
   path('invoice/<int:pk>', Invoice.as_view(), name = 'invoice'),
   path('invoice/<int:pk>/pdf/', views.generate_invoice_pdf, name='generate_invoice_pdf'),
]
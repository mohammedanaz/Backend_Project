from django.urls import path
from .views import AdminHome, AdminUsers, AdminProducts

app_name = 'custom_admin'

urlpatterns = [
    path('', AdminHome.as_view(), name = 'admin_home'),
    path('users/', AdminUsers.as_view(), name = 'admin_users'),
    path('products/', AdminProducts.as_view(), name = 'admin_products'),
]   
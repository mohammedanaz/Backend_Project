from django.urls import path
from .views import AdminHome, AdminUsers, AdminProducts, AdminProductEdit

app_name = 'custom_admin'

urlpatterns = [
    path('', AdminHome.as_view(), name = 'admin_home'),
    path('users/', AdminUsers.as_view(), name = 'admin_users'),
    path('products/', AdminProducts.as_view(), name = 'admin_products'),
    path('products/<int:pk>/edit/', AdminProductEdit.as_view(), name = 'admin_product_edit'),
]   
from django.urls import path
from .views import AdminHome, AdminUsers, AdminProducts, AdminProductEdit, AdminProductDelete

app_name = 'custom_admin'

urlpatterns = [
    path('', AdminHome.as_view(), name = 'admin_home'),
    path('users/', AdminUsers.as_view(), name = 'admin_users'),
    path('products/', AdminProducts.as_view(), name = 'admin_products'),
    path('products/<int:id>/edit/', AdminProductEdit.as_view(), name = 'admin_product_edit'),
    path('products/delete/', AdminProductDelete.as_view(), name = 'admin_product_delete'),
]   
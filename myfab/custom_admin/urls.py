from django.urls import path
from .views import AdminHome, AdminUsers, AdminUserSearch, AdminProducts, AdminProductEdit, AdminProductDelete, AdminProductAdd
from .views import AdminCategories, AdminCategoryEdit, AdminCategoryAdd, AdminCategoryDelete
from .views import AdminUsages, AdminUsageEdit, AdminUsageAdd, AdminUsageDelete
from .views import AdminMeasurements, AdminMeasurementAdd, AdminMeasurementEdit, AdminMeasurementDelete, AdminProductSearch
from .views import AdminOrders, AdminOrderSearch, AdminReturnsView, AdminReturnSearch, SalesReport, Banner, BannerEdit
app_name = 'custom_admin'

urlpatterns = [
    path('', AdminHome.as_view(), name = 'admin_home'),
    path('users/', AdminUsers.as_view(), name = 'admin_users'),
    path('users/search/', AdminUserSearch.as_view(), name = 'admin_user_search'),
    path('products/', AdminProducts.as_view(), name = 'admin_products'),
    path('products/search/', AdminProductSearch.as_view(), name = 'admin_product_search'),
    path('products/<int:pk>/edit/', AdminProductEdit.as_view(), name = 'admin_product_edit'),
    path('products/<int:pk>/delete/', AdminProductDelete.as_view(), name = 'admin_product_delete'),
    path('products/add/', AdminProductAdd.as_view(), name='admin_product_add'),
    path('categories/', AdminCategories.as_view(), name='admin_categories'),
    path('categories/<int:pk>/edit/', AdminCategoryEdit.as_view(), name='admin_category_edit'),
    path('categories/add/', AdminCategoryAdd.as_view(), name='admin_category_add'),
    path('categories/<int:pk>/delete/', AdminCategoryDelete.as_view(), name='admin_category_delete'),
    path('usages/', AdminUsages.as_view(), name='admin_usages'),
    path('usages/<int:pk>/edit/', AdminUsageEdit.as_view(), name='admin_usage_edit'),
    path('usages/add/', AdminUsageAdd.as_view(), name='admin_usage_add'),
    path('usages/<int:pk>/delete/', AdminUsageDelete.as_view(), name='admin_usage_delete'),
    path('measurements/', AdminMeasurements.as_view(), name='admin_measurements'),
    path('measurements/<int:pk>/edit/', AdminMeasurementEdit.as_view(), name='admin_measurement_edit'),
    path('measurements/add/', AdminMeasurementAdd.as_view(), name='admin_measurement_add'),
    path('measurements/<int:pk>/delete/', AdminMeasurementDelete.as_view(), name='admin_measurement_delete'),
    path('orders/', AdminOrders.as_view(), name = 'admin_orders'),
    path('orders/search/', AdminOrderSearch.as_view(), name = 'admin_order_search'),
    path('returns/', AdminReturnsView.as_view(), name = 'admin_order_return'),
    path('returns/search/', AdminReturnSearch.as_view(), name = 'admin_return_search'),
    path('sales_report/', SalesReport.as_view(), name='sales_report'),
    path('banners/', Banner.as_view(), name='admin_banners'),
    path('banner_edit/', BannerEdit.as_view(), name='admin_banner_edit'),
]   
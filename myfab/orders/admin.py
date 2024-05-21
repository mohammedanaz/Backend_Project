from django.contrib import admin
from .models import Cart, Order, ReturnOrder

# Register your models here.

class CartAdmin(admin.ModelAdmin):
    list_display = ('id','customer_id', 'product_id', 'order_type', 'qty', 'price')


admin.site.register(Cart, CartAdmin)
admin.site.register(Order)
admin.site.register(ReturnOrder)

from django.contrib import admin
from .models import Cart, Order

# Register your models here.

class CartAdmin(admin.ModelAdmin):
    list_display = ('id','customer_id', 'product_id','qty', 'price')

admin.site.register(Cart, CartAdmin)

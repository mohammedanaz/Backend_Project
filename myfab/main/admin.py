from django.contrib import admin
from .models import Product, Usage

# Register your models here.

admin.site.register(Product)
admin.site.register(Usage)
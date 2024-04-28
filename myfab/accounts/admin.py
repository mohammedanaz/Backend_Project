from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class CustomUserAdmin(UserAdmin):
    model = CustomUser
##### to add phone number to user list in admin ui#####
    list_display = ['username', 'email', 'phone_number', 'first_name', 'last_name', 'is_staff']

##### (override fieldsets attribute) to add phone number to user details section of admin ui#####
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )



admin.site.register(CustomUser, CustomUserAdmin)

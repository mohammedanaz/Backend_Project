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
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

### Override the form fields in admin ui to mark groups and user_permissions as not required when editing a user ###
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['groups'].required = False
        form.base_fields['user_permissions'].required = False
        return form

admin.site.register(CustomUser, CustomUserAdmin)

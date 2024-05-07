from django.contrib import admin
from .models import Product, Usage, Category, CategoryChoice, Measurement
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse



# Register your models here.

class CategoryChoiceAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'category', 'image')

class UsageAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'image', 'gender')

class ProductAdmin(admin.ModelAdmin):
    ''' To confirm that each category of a product dont have 
         multiple choices (rg. material = cotton and polyester)'''
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'category_choices':
            kwargs['queryset'] = db_field.related_model.objects.all()

        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        
        ''' To confirm that each category of a product dont have 
         multiple choices (rg. material = cotton and polyester)'''
        
        category_counts = {}
        for choice in form.cleaned_data['category_choices']:
            category = choice.category.name
            if category in category_counts:
                raise ValidationError(f"Multiple choices from category '{category}' are not allowed.")
            category_counts[category] = 1

        super().save_model(request, obj, form, change)


    

admin.site.register(Product, ProductAdmin)
admin.site.register(Usage, UsageAdmin)
admin.site.register(Category)
admin.site.register(CategoryChoice, CategoryChoiceAdmin)
admin.site.register(Measurement)
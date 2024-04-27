from django.contrib import admin
from .models import Product, Usage, Category, CategoryChoice
from django import forms



# Register your models here.

class CategoryChoiceAdmin(admin.ModelAdmin):
    list_display = ('id','choices', 'category', 'image')

class UsageAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'image', 'gender')


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProductAdminForm, self).__init__(*args, **kwargs)
        # Add select fields for all categories
        for category in Category.objects.all():
            choices = CategoryChoice.objects.filter(category=category)
            choices_list = [(choice.choices, choice.choices) for choice in choices]
            self.fields[f'{category.name}'] = forms.ChoiceField(
                choices=choices_list,
                label=category.name,
                required=False,  # Make the dropdown optional
            )
        # Update fields in Meta dynamically (if you prefer)
        self.Meta.fields += [f'{category.name}' for category in Category.objects.all()]


class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    

admin.site.register(Product, ProductAdmin)
admin.site.register(Usage, UsageAdmin)
admin.site.register(Category)
admin.site.register(CategoryChoice, CategoryChoiceAdmin)
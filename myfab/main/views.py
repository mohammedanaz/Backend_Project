from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from .models import Usage, Category, CategoryChoice, Product


# Create your views here.



############################### Home Men CBV ######################################

class Home(View):
    def get(self, request):
        
        usages = Usage.objects.filter(gender='M')  # Filter usages with male gender
        usage_list = list(usages)

        categories_with_img = Category.objects.filter(categorychoice__image__isnull=False).distinct()
        categories_filtered = categories_with_img.exclude(name='gender') # to remove gender which is not filtered out
        choices_with_img = CategoryChoice.objects.filter(image__isnull=False)
        choices_filtered = choices_with_img.exclude(name = 'male') # to remove male which is not filtered out
        dict = {}
        for category in categories_filtered:
            choices = choices_filtered.filter(category = category)
            dict[category.name] = choices
        context = {'usages': usage_list,
                   'categories_filtered': categories_filtered,
                   'choices_filtered': choices_filtered,
                   'dict': dict
                   }

        return render(request, 'home.html', context)
    


############################### Home Women CBV ######################################

class HomeWomen(View):
    def get(self, request):
        
        usages = Usage.objects.filter(gender='F')  # Filter usages with female gender
        usage_list = list(usages)

        categories_with_img = Category.objects.filter(categorychoice__image__isnull=False).distinct()
        categories_filtered = categories_with_img.exclude(name='gender') # to remove gender which is not filtered out
        choices_with_img = CategoryChoice.objects.filter(image__isnull=False)
        choices_filtered = choices_with_img.exclude(name = 'male') # to remove male which is not filtered out
        dict = {}
        for category in categories_filtered:
            choices = choices_filtered.filter(category = category)
            dict[category.name] = choices
        context = {'usages': usage_list,
                   'categories_filtered': categories_filtered,
                   'choices_filtered': choices_filtered,
                   'dict': dict
                   }

        return render(request, 'home_women.html', context)
    

############################### Products CBV ######################################

class ProductPage(View):

    def get(self, request):
        return render(request, 'products.html')
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from .models import Usage, Category, CategoryChoice, Product
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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
        products_list = Product.objects.all()
        paginator = Paginator(products_list, 9)
        page_number = request.GET.get('page')
        try:
            products = paginator.page(page_number)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        categories = Category.objects.all()
        category_choice_dict = {}
        for category in categories:
            choice_obj = CategoryChoice.objects.filter(category=category)
            choices_list = [choice.name for choice in choice_obj]
            category_choice_dict[category.name] = choices_list
        context = {'products': products,
                   'category_choice_dict': category_choice_dict
                   }
        return render(request, 'products.html', context)
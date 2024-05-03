from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from .models import Usage, Category, CategoryChoice, Product
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


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
        # Making an all product query set
        products = Product.objects.all()

        # Section for handling filter queries
        selected_choices = request.GET.getlist('choice')
        selected_category_choice_dict = {}
        for choice in selected_choices:
            choice_obj = CategoryChoice.objects.get(name=choice)
            selected_category = choice_obj.category.name
            if selected_category in  selected_category_choice_dict:
                selected_category_choice_dict[selected_category] += [choice]
            else:
                selected_category_choice_dict[selected_category] = [choice]
        if selected_category_choice_dict:
            for selected_category, choices in selected_category_choice_dict.items():
                q_obj = Q()
                for choice in choices:
                    q_obj |= Q(category_choices__name=choice)
                products = products.filter(q_obj)
        product_count = products.count()
        # Section For pagination
        paginator = Paginator(products, 9)
        page_number = request.GET.get('page')
        try:
            paged_products = paginator.page(page_number)
        except PageNotAnInteger:
            paged_products = paginator.page(1)
        except EmptyPage:
            paged_products = paginator.page(paginator.num_pages)

        # Section For listing category and choices for filters
        categories = Category.objects.all()
        category_choice_dict = {}
        for category in categories:
            choice_obj = CategoryChoice.objects.filter(category=category)
            choices_list = [choice.name for choice in choice_obj]
            category_choice_dict[category.name] = choices_list

        # Context data
        context = {'products': paged_products,
                   'product_count': product_count,
                   'category_choice_dict': category_choice_dict,
                   'selected_choices': selected_choices
                   }
        return render(request, 'products.html', context)
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView
from .models import Usage, Category, CategoryChoice, Product
from orders.models import Cart
from main.models import BannerMen, BannerWomen
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Sum
from django.db.models.functions import Lower


# Create your views here.



############################### Home Men CBV ######################################

class Home(View):
    def get(self, request):
        
        usages = Usage.objects.filter(gender='M')  # Filter usages with male gender
        usage_list = list(usages)

        categories_with_img = Category.objects.filter(categorychoice__image__isnull=False).distinct()
        categories_filtered = categories_with_img.exclude(name__iexact='gender') # to remove gender which is not filtered out
        choices_with_img = CategoryChoice.objects.filter(image__isnull=False)
        choices_filtered = choices_with_img.exclude(name__iexact = 'male').exclude(name__iexact='female') # to remove male which is not filtered out
        dict = {}
        for category in categories_filtered:
            choices = choices_filtered.filter(category = category)
            dict[category.name] = choices

        # Make cart items for context
        user= request.user
        if user.is_authenticated:
            cart_items = Cart.objects.filter(customer_id=user)
            cart_count = cart_items.count()
            total_price = cart_items.aggregate(total_price=Sum('price'))['total_price'] or 0
        else:
            cart_items = []
            cart_count = 0
            total_price = 0
            
        banners = BannerMen.objects.all()

        context = {
                    'usages': usage_list,
                    'categories_filtered': categories_filtered,
                    'choices_filtered': choices_filtered,
                    'dict': dict,
                    'cart_items': cart_items,
                    'cart_count': cart_count,
                    'total_price': total_price,
                    'banners': banners,
                    }
        return render(request, 'home.html', context)
    



############################### Home Women CBV ######################################

class HomeWomen(View):
    def get(self, request):
        
        usages = Usage.objects.filter(gender='F')  # Filter usages with female gender
        usage_list = list(usages)

        categories_with_img = Category.objects.filter(categorychoice__image__isnull=False).distinct()
        categories_filtered = categories_with_img.exclude(name__iexact='gender') # to remove gender which is not filtered out
        choices_with_img = CategoryChoice.objects.filter(image__isnull=False)
        choices_filtered = choices_with_img.exclude(name__iexact = 'male').exclude(name__iexact='female') # to remove male which is not filtered out
        dict = {}
        for category in categories_filtered:
            choices = choices_filtered.filter(category = category)
            dict[category.name] = choices

        # Make cart items for context
        user= request.user
        if user.is_authenticated:
            cart_items = Cart.objects.filter(customer_id=user)
            cart_count = cart_items.count()
            total_price = cart_items.aggregate(total_price=Sum('price'))['total_price'] or 0
        else:
            cart_items = []
            cart_count = 0
            total_price = 0

        banners = BannerWomen.objects.all()

        context = {
                    'usages': usage_list,
                    'categories_filtered': categories_filtered,
                    'choices_filtered': choices_filtered,
                    'dict': dict,
                    'cart_items': cart_items,
                    'cart_count': cart_count,
                    'total_price': total_price,
                    'banners': banners,
                   }

        return render(request, 'home_women.html', context)
    

############################### Products CBV ######################################

class ProductPage(View):

    def get(self, request):
        '''
        To render Products display page. with pagination, search, sort, 
        filter logics.
        '''
        # Making an all product query set
        products = Product.objects.all()

        # Section for handling search query
        search_query = request.GET.get('search', None)
        if search_query:
            products = products.filter(Q(name__icontains=search_query))

        # Section for handling filter queries
        selected_choices = request.GET.getlist('choice', None)
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

        # Section For sorting
        sort_by = request.GET.get('sort', None)
        if sort_by == 'newest':
            products = products.order_by('-add_date')
        elif sort_by == 'name_asc':
            products = products.order_by(Lower('name'))
        elif sort_by == 'name_dsc':
            products = products.order_by(Lower('name')).reverse()
        elif sort_by == 'lowest':
            products = products.order_by('price')
        elif sort_by == 'highest':
            products = products.order_by('-price')
        

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
        
        # Make cart items for context
        user= request.user
        if user.is_authenticated:
            cart_items = Cart.objects.filter(customer_id=user)
            cart_count = cart_items.count()
            total_price = cart_items.aggregate(total_price=Sum('price'))['total_price'] or 0
        else:
            cart_items = []
            cart_count = 0
            total_price = 0

        # Context data
        context = {
                    'products': paged_products,
                    'product_count': product_count,
                    'category_choice_dict': category_choice_dict,
                    'selected_choices': selected_choices,
                    'sort_by': sort_by,
                    'search_query': search_query,
                    'cart_items': cart_items,
                    'cart_count': cart_count,
                    'total_price': total_price,
                   }
        return render(request, 'products.html', context)
    

    ############################### Products Details CBV ######################################

class ProductDetailsPage(DetailView):
    model = Product
    template_name = 'product_details.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = context['product']
    
        usages = product.usages.all()
        context['usages'] = usages
        
        measurements = {}
        for usage in usages:
            measurements[usage.pk] = list(usage.measurements.all())
        context['measurements_dict'] = measurements

        # Make cart items for context
        user= self.request.user
        if user.is_authenticated:
            cart_items = Cart.objects.filter(customer_id=user)
            context['cart_items'] = cart_items
            cart_count = cart_items.count()
            context['cart_count'] = cart_count
            total_price = cart_items.aggregate(total_price=Sum('price'))['total_price'] or 0
            context['total_price'] = total_price
        
        return context
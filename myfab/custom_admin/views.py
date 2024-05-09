from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
import json
from django.views import View
from django.views.generic import UpdateView, DeleteView
from django.views.generic.edit import CreateView
from accounts.models import CustomUser
from main.models import Product, Category, CategoryChoice, Usage, Measurement
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.
################################### Admin Home ####################################
class AdminHome(View):
    def get(self, request):
        users = CustomUser.objects.all()[:5]
        context = {'users': users}
        return render(request, 'admin_home.html', context)
    
    def post(self, request):
        json_data = json.loads(request.body)

        if 'user_id' in json_data:  # Check for user_id in json data
                user_id = json_data.get('user_id')
                is_active = json_data.get('is_active')
                try:
                    user = CustomUser.objects.get(id=user_id)
                    user.is_active = is_active
                    user.save()
                    return JsonResponse({'success': True})
                except CustomUser.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'User not found'})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': str(e)})
        else:
            print('Missing user_id in request data')
            return JsonResponse({'success': False, 'error': 'Missing user_id in request data'})


################################### Admin Users ####################################

class AdminUsers(View):
    def get(self, request):
        users_list = CustomUser.objects.all()
        paginator = Paginator(users_list, 10) 
        page_number = request.GET.get('page')
        try:
            users = paginator.page(page_number)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)
        context = {'users': users}
        return render(request, 'admin_users.html', context)

################################### Admin Products ####################################

class AdminProducts(View):
    def get(self, request):
        products = Product.objects.all()
        paginator = Paginator(products, 10) 
        page_number = request.GET.get('page')
        try:
            paged_products = paginator.page(page_number)
        except PageNotAnInteger:
            paged_products = paginator.page(1)
        except EmptyPage:
             paged_products = paginator.page(paginator.num_pages)
        # Calculate the starting serial number for the current page
        start_serial_number = (paged_products.number - 1) * paginator.per_page + 1
        
        # Create a list to hold the serial numbers for the current page
        serial_numbers = list(range(start_serial_number, start_serial_number + len(paged_products)))
        zipped_data = zip(serial_numbers, paged_products)

        context = {'zipped_data': zipped_data, 'products': paged_products}
        return render(request, 'admin_products.html', context)
    

################################### Admin Product Search ####################################

class AdminProductSearch(View):
    def get(self, request):
        query = request.GET.get('query', '')
        page_number = request.GET.get('page', 1)
        products = Product.objects.filter(name__icontains=query)
        paginator = Paginator(products, 10)

        try:
            paged_products = paginator.page(page_number)
        except PageNotAnInteger:
            paged_products = paginator.page(1)
        except EmptyPage:
            paged_products = paginator.page(paginator.num_pages)

        # Calculate the starting serial number for the current page
        start_serial_number = (paged_products.number - 1) * paginator.per_page + 1

        # Create a list to hold the serial numbers for the current page
        serial_numbers = list(range(start_serial_number, start_serial_number + len(paged_products)))
        serial_numbers.reverse() # reverse list of page Sr number for poping

        data = [{'name': product.name, 
                 'price': product.price, 
                 'qty': product.qty, 
                 'add_date': product.add_date, 
                 'image_url': product.image.url, 
                 'id': product.id,
                 'serial_number':serial_numbers.pop()
                 } for product in paged_products]
        return JsonResponse({'data': data, 'has_previous': paged_products.has_previous(), 'has_next': paged_products.has_next(), 'pages': paginator.num_pages}, safe=False)


################################### Admin Product Edit ####################################

class AdminProductEdit(UpdateView):
    model = Product
    fields = ['name', 'price', 'image', 'description', 'qty', 'is_active', 'usages', 'category_choices']
    template_name = 'admin_product_edit.html'

    # To pass prev page url into the context to use with cancel btn
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['previous_url'] = self.request.META.get('HTTP_REFERER', reverse('custom_admin:admin_products'))
        return context
    
    # To redirect to prev page after deletion
    def get_success_url(self):
        return self.request.POST.get('next', self.success_url)


################################### Admin Product Delete ####################################

class AdminProductDelete(DeleteView):
    model = Product
    template_name = 'admin_product_confirm_delete.html'

    # To pass prev page url into the context to use with cancel btn
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['previous_url'] = self.request.META.get('HTTP_REFERER', reverse('custom_admin:admin_products'))
        return context
    
    # To redirect to prev page after deletion
    def get_success_url(self):
        return self.request.POST.get('next', self.success_url)
    

################################### Admin Product Add ####################################

class AdminProductAdd(CreateView):
    model = Product
    fields = ['name', 'price', 'image', 'description', 'qty', 'is_active', 'usages', 'category_choices']
    template_name = 'admin_product_add.html'  

    # To pass prev page url into the context to use with cancel btn
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['previous_url'] = self.request.META.get('HTTP_REFERER', reverse('custom_admin:admin_products'))
        return context
    
    # To redirect to prev page after deletion
    def get_success_url(self):
        return self.request.POST.get('next', self.success_url)

################################### Admin Categories ####################################

class AdminCategories(View):
    def get(self, request):
        categories = Category.objects.all()
        context = {'categories': categories}
        return render(request, 'admin_categories.html', context)

################################### Admin Category Edit ####################################

class AdminCategoryEdit(UpdateView):
    model = Category
    fields = ['name']
    template_name = 'admin_category_edit.html'

    # To pass prev page url into the context to use with cancel btn
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['previous_url'] = self.request.META.get('HTTP_REFERER', reverse('custom_admin:admin_categories'))
        return context
    
    # To redirect to prev page after deletion
    def get_success_url(self):
        return self.request.POST.get('next', self.success_url)

################################### Admin Category Add ####################################

class AdminCategoryAdd(CreateView):
    model = Category
    fields = ['name']
    template_name = 'admin_category_add.html'  

    # To pass prev page url into the context to use with cancel btn
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['previous_url'] = self.request.META.get('HTTP_REFERER', reverse('custom_admin:admin_categories'))
        return context
    
    # To redirect to prev page after deletion
    def get_success_url(self):
        return self.request.POST.get('next', self.success_url)



################################### Admin Category Delete ####################################

class AdminCategoryDelete(DeleteView):
    model = Category
    template_name = 'admin_category_confirm_delete.html'

    # To pass prev page url into the context to use with cancel btn
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['previous_url'] = self.request.META.get('HTTP_REFERER', reverse('custom_admin:admin_categories'))
        return context
    
    # To redirect to prev page after deletion
    def get_success_url(self):
        return self.request.POST.get('next', self.success_url)


################################### Admin Usage types ####################################

class AdminUsages(View):
    def get(self, request):
        usages = Usage.objects.all()
        paginator = Paginator(usages, 6) 
        page_number = request.GET.get('page')
        try:
            paged_usages = paginator.page(page_number)
        except PageNotAnInteger:
            paged_usages = paginator.page(1)
        except EmptyPage:
             paged_usages = paginator.page(paginator.num_pages)
        # Calculate the starting serial number for the current page
        start_serial_number = (paged_usages.number - 1) * paginator.per_page + 1
        
        # Create a list to hold the serial numbers for the current page
        serial_numbers = list(range(start_serial_number, start_serial_number + len(paged_usages)))
        zipped_data = zip(serial_numbers, paged_usages)
        context = {'zipped_data': zipped_data,'usages': paged_usages}
        return render(request, 'admin_usages.html', context)

################################### Admin Usage Edit ####################################

class AdminUsageEdit(UpdateView):
    model = Usage
    fields = ['name', 'image', 'gender', 'measurements']
    template_name = 'admin_usage_edit.html'

    # To pass prev page url into the context to use with cancel btn
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['previous_url'] = self.request.META.get('HTTP_REFERER', reverse('custom_admin:admin_usages'))
        return context
    
    # To redirect to prev page after deletion
    def get_success_url(self):
        return self.request.POST.get('next', self.success_url)

################################### Admin Usage Add ####################################

class AdminUsageAdd(CreateView):
    model = Usage
    fields = ['name', 'image', 'gender', 'measurements']
    template_name = 'admin_usage_add.html'  

    # To pass prev page url into the context to use with cancel btn
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['previous_url'] = self.request.META.get('HTTP_REFERER', reverse('custom_admin:admin_usages'))
        return context
    
    # To redirect to prev page after deletion
    def get_success_url(self):
        return self.request.POST.get('next', self.success_url)



################################### Admin Usage Delete ####################################

class AdminUsageDelete(DeleteView):
    model = Usage
    template_name = 'admin_usage_confirm_delete.html'

    # To pass prev page url into the context to use with cancel btn
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['previous_url'] = self.request.META.get('HTTP_REFERER', reverse('custom_admin:admin_usages'))
        return context
    
    # To redirect to prev page after deletion
    def get_success_url(self):
        return self.request.POST.get('next', self.success_url)

################################### Admin Measurements types ####################################

class AdminMeasurements(View):
    def get(self, request):
        measurements = Measurement.objects.all()
        paginator = Paginator(measurements, 6) 
        page_number = request.GET.get('page')
        try:
            paged_measurements = paginator.page(page_number)
        except PageNotAnInteger:
            paged_measurements = paginator.page(1)
        except EmptyPage:
             paged_measurements = paginator.page(paginator.num_pages)
        # Calculate the starting serial number for the current page
        start_serial_number = (paged_measurements.number - 1) * paginator.per_page + 1
        
        # Create a list to hold the serial numbers for the current page
        serial_numbers = list(range(start_serial_number, start_serial_number + len(paged_measurements)))
        zipped_data = zip(serial_numbers, paged_measurements)
        context = {'zipped_data': zipped_data,'measurements': paged_measurements}
        return render(request, 'admin_measurements.html', context)

################################### Admin Usage Edit ####################################

class AdminMeasurementEdit(UpdateView):
    model = Measurement
    fields = ['name']
    template_name = 'admin_measurement_edit.html'

    # To pass prev page url into the context to use with cancel btn
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['previous_url'] = self.request.META.get('HTTP_REFERER', reverse('custom_admin:admin_measurements'))
        return context
    
    # To redirect to prev page after deletion
    def get_success_url(self):
        return self.request.POST.get('next', self.success_url)

################################### Admin Usage Add ####################################

class AdminMeasurementAdd(CreateView):
    model = Measurement
    fields = ['name']
    template_name = 'admin_measurement_add.html'  

    # To pass prev page url into the context to use with cancel btn
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['previous_url'] = self.request.META.get('HTTP_REFERER', reverse('custom_admin:admin_measurements'))
        return context
    
    # To redirect to prev page after deletion
    def get_success_url(self):
        return self.request.POST.get('next', self.success_url)



################################### Admin Usage Delete ####################################

class AdminMeasurementDelete(DeleteView):
    model = Measurement
    template_name = 'admin_measurement_confirm_delete.html'

    # To pass prev page url into the context to use with cancel btn
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['previous_url'] = self.request.META.get('HTTP_REFERER', reverse('custom_admin:admin_measurements'))
        return context
    
    # To redirect to prev page after deletion
    def get_success_url(self):
        return self.request.POST.get('next', self.success_url)


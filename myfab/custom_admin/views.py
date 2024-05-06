from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
import json
from django.views import View
from django.views.generic import UpdateView
from django.views.generic.edit import CreateView
from accounts.models import CustomUser
from main.models import Product
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
    
################################### Admin Product Edit ####################################

class AdminProductEdit(UpdateView):
    model = Product
    fields = ['name', 'price', 'image', 'description', 'qty', 'is_active', 'usages', 'category_choices']
    template_name = 'admin_product_edit.html'
    success_url = reverse_lazy('custom_admin:admin_products')


################################### Admin Product Delete ####################################

class AdminProductDelete(View):

    def post(self, request):
        product_id = request.POST.get('id')

        # Retrieve the product instance from the database
        product = get_object_or_404(Product, pk=product_id)
        
        # Delete the product
        product.delete()
        
        print(f'Item with id = {product_id} deleted successfully')
        return redirect(reverse('custom_admin:admin_products'))
    

################################### Admin Product Add ####################################

class AdminProductAdd(CreateView):
    model = Product
    fields = ['name', 'price', 'image', 'description', 'qty', 'is_active', 'usages', 'category_choices']
    template_name = 'admin_product_add.html'  
    success_url = reverse_lazy('custom_admin:admin_products')  
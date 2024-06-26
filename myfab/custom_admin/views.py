from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse
import json
from django.views import View
from django.views.generic import UpdateView, DeleteView
from django.views.generic.edit import CreateView
from accounts.models import CustomUser
from main.models import Product, Category, Usage, Measurement, BannerMen, BannerWomen
from orders.models import  ReturnOrder, Order
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db.models.functions import ExtractMonth, ExtractYear
import calendar
from datetime import datetime, timedelta
from django.db.models import Count, Sum
import xlsxwriter
from io import BytesIO
from PIL import Image
import imghdr
import math

# Create your views here.
################################### Admin Home ####################################
class AdminHome(View):
    '''
    To render the admin home page with charts.
    '''
    def get(self, request):
        # This quer generates a list of dicts that contain
        # {'month': values, 'order_count': values} format.
        unique_years = (
            Order.objects
            .annotate(year=ExtractYear('add_date'))
            .values_list('year', flat=True)
            .distinct()
            )
        current_year = datetime.now().year
        orders = (
            Order.objects
            .annotate(year=ExtractYear('add_date')).filter(year=current_year)
            .annotate(month=ExtractMonth('add_date'))
            .values('month')  # Select only the 'month' field
            .annotate(order_count=Count('id'))  # Count the number of orders per month
            .order_by('month')  # Order by month 
        )

        months_orders = {
            'Jan': 0, 'Feb': 0, 'Mar': 0, 'Apr': 0, 'May': 0, 'Jun': 0,
            'Jul': 0, 'Aug': 0, 'Sep': 0, 'Oct': 0, 'Nov': 0, 'Dec': 0
        }

        for order in orders:
            month_abbr = calendar.month_name[order['month']][:3]
            months_orders[month_abbr] = order['order_count']

        sales = (
            Order.objects
            .annotate(year=ExtractYear('add_date')).filter(year=current_year)
            .annotate(month=ExtractMonth('add_date'))
            .values('month')  
            .annotate(sales=Sum('price'))  
            .order_by('month') 
        )

        months_sales = {
            'Jan': 0, 'Feb': 0, 'Mar': 0, 'Apr': 0, 'May': 0, 'Jun': 0,
            'Jul': 0, 'Aug': 0, 'Sep': 0, 'Oct': 0, 'Nov': 0, 'Dec': 0
        }

        for sale in sales:
            month_abbr = calendar.month_name[sale['month']][:3]
            months_sales[month_abbr] = sale['sales']

        recent_orders = (
            Order.objects.all()
            .order_by('-add_date')[:5]
        )
        
        context = {
            'months_orders': months_orders,
            'months_sales': months_sales,
            'current_year': current_year,
            'unique_years': unique_years,
            'recent_orders': recent_orders,
                   }
        return render(request, 'admin_home.html', context)
    
    def post(self, request):
        '''
        To handle post axios request to change the year for chart view.
        '''
        json_data = json.loads(request.body)
        requested_year = json_data.get('year')

        orders = (
            Order.objects
            .annotate(year=ExtractYear('add_date')).filter(year=requested_year)
            .annotate(month=ExtractMonth('add_date'))
            .values('month')  # Select only the 'month' field
            .annotate(order_count=Count('id'))  # Count the number of orders per month
            .order_by('month')  # Order by month 
        )

        months_orders = {
            'Jan': 0, 'Feb': 0, 'Mar': 0, 'Apr': 0, 'May': 0, 'Jun': 0,
            'Jul': 0, 'Aug': 0, 'Sep': 0, 'Oct': 0, 'Nov': 0, 'Dec': 0
        }

        for order in orders:
            month_abbr = calendar.month_name[order['month']][:3]
            months_orders[month_abbr] = order['order_count']
        
        sales = (
            Order.objects
            .annotate(year=ExtractYear('add_date')).filter(year=requested_year)
            .annotate(month=ExtractMonth('add_date'))
            .values('month')  
            .annotate(sales=Sum('price'))  
            .order_by('month') 
        )

        months_sales = {
            'Jan': 0, 'Feb': 0, 'Mar': 0, 'Apr': 0, 'May': 0, 'Jun': 0,
            'Jul': 0, 'Aug': 0, 'Sep': 0, 'Oct': 0, 'Nov': 0, 'Dec': 0
        }

        for sale in sales:
            month_abbr = calendar.month_name[sale['month']][:3]
            months_sales[month_abbr] = sale['sales']

        return JsonResponse({'months_orders': months_orders, 'months_sales': months_sales})


################################### Admin Users ####################################

class AdminUsers(View):
    '''
    get method is to render admin user list page.
    post method is to handle json data to change status.
    '''
    def get(self, request):
        users = CustomUser.objects.all()
        paginator = Paginator(users, 10) 
        page_number = request.GET.get('page')
        try:
            paged_users = paginator.page(page_number)
        except PageNotAnInteger:
            paged_users = paginator.page(1)
        except EmptyPage:
            paged_users = paginator.page(paginator.num_pages)

        # Calculate the starting serial number for the current page
        start_serial_number = (paged_users.number - 1) * paginator.per_page + 1
        
        # Create a list to hold the serial numbers for the current page
        serial_numbers = list(range(start_serial_number, start_serial_number + len(paged_users)))
        zipped_data = zip(serial_numbers, paged_users)
        
        context = {'zipped_data': zipped_data, 'users': paged_users}
        return render(request, 'admin_users.html', context)
    
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
        return JsonResponse({'data': data, 'has_previous': paged_products.has_previous(), 
                             'has_next': paged_products.has_next(), 
                             'pages': paginator.num_pages})


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
    

################################### Admin Orders ####################################

class AdminOrders(View):
    '''
    post method in this view is used to recieve axios req for
    order status change to update DB. validate before change status.
    Get method is to render order list page. 
    '''
    def get(self, request):
        orders = Order.objects.all().order_by('-add_date')
        paginator = Paginator(orders, 10) 
        page_number = request.GET.get('page')
        try:
            paged_orders = paginator.page(page_number)
        except PageNotAnInteger:
            paged_orders = paginator.page(1)
        except EmptyPage:
            paged_orders = paginator.page(paginator.num_pages)
        # Calculate the starting serial number for the current page
        start_serial_number = (paged_orders.number - 1) * paginator.per_page + 1
        
        # Create a list to hold the serial numbers for the current page
        serial_numbers = list(range(start_serial_number, start_serial_number + len(paged_orders)))
        zipped_data = zip(serial_numbers, paged_orders)

        context = {'zipped_data': zipped_data, 'orders': paged_orders}
        return render(request, 'admin_orders.html', context)
    
    def post(self, request):
        json_data = json.loads(request.body)

        order_id = json_data.get('order_id')
        if order_id:
            new_status = json_data.get('new_status')
            order = Order.objects.get(id=order_id)
            old_status = order.status
            if old_status == 'C' or old_status == 'R':
                return JsonResponse({
                    'error-msg': 'cannot change Cancelled or Returned order.',
                    'oldStatus': old_status
                    }, status=400)
            elif new_status == 'P':
                return JsonResponse({
                    'error-msg': 'cannot change back to Pending.',
                    'oldStatus': old_status
                    }, status=400)
            elif new_status == 'S' and old_status == 'D':
                return JsonResponse({
                    'error-msg': 'order already  Delivered.',
                    'oldStatus': old_status
                    }, status=400)
            elif new_status == 'C' and old_status == 'D':
                return JsonResponse({
                    'error-msg': 'order already Delivered. You can change to Returned',
                    'oldStatus': old_status
                    }, status=400)
            else:
                order.status = new_status
                order.save()
                return JsonResponse({'success': True, 'success_msg': 'Order status updated.'})
        else:
            return JsonResponse({'success': False, 'error_msg': 'Order id not found.'})



################################### Admin Orders Search ####################################

class AdminOrderSearch(View):
    def get(self, request):
        query = request.GET.get('query', '')
        order_status = request.GET.get('orderStatus')
        page_number = request.GET.get('page', 1)
        # Filter order list as per status selected 
        if order_status == 'All':
            orders = (
                Order.objects
                .filter(Q(customer_id__username__icontains=query) | Q(id__icontains=query))
                .order_by('-add_date')
            )
        else:
            order_status_map = {
                'Pending': 'P',
                'Shipping': 'S',
                'Delivered': 'D',
                'Cancelled': 'C'
            }
            status = order_status_map.get(order_status)
            orders = (
                Order.objects
                .filter(status=status)
                .filter(Q(customer_id__username__icontains=query) | Q(id__icontains=query))
                .order_by('-add_date')
            )
        # Pagination
        paginator = Paginator(orders, 10)
        try:
            paged_orders = paginator.page(page_number)
        except PageNotAnInteger:
            paged_orders = paginator.page(1)
        except EmptyPage:
            paged_orders = paginator.page(paginator.num_pages)

        # Calculate the starting serial number for the current page
        start_serial_number = (paged_orders.number - 1) * paginator.per_page + 1

        # Create a list to hold the serial numbers for the current page
        serial_numbers = list(range(start_serial_number, start_serial_number + len(paged_orders)))
        serial_numbers.reverse() # reverse list of page Sr number for poping

        data = [{'username': order.customer_id.username, 
                 'price': order.price, 
                 'qty': order.quantity, 
                 'add_date': order.add_date,
                 'status': order.status,
                 'id': order.id,
                 'serial_number':serial_numbers.pop()
                 } for order in paged_orders]
        return JsonResponse({'data': data, 'has_previous': paged_orders.has_previous(), 
                             'has_next': paged_orders.has_next(), 
                             'pages': paginator.num_pages})
    

    ################################### Admin Users Search ####################################

class AdminUserSearch(View):
    def get(self, request):
        query = request.GET.get('query', '')
        page_number = request.GET.get('page', 1)
        users = CustomUser.objects.filter(Q(first_name__icontains=query) | Q(username__icontains=query))
        paginator = Paginator(users, 10)

        try:
            paged_users = paginator.page(page_number)
        except PageNotAnInteger:
            paged_users = paginator.page(1)
        except EmptyPage:
            paged_users = paginator.page(paginator.num_pages)

        # Calculate the starting serial number for the current page
        start_serial_number = (paged_users.number - 1) * paginator.per_page + 1

        # Create a list to hold the serial numbers for the current page
        serial_numbers = list(range(start_serial_number, start_serial_number + len(paged_users)))
        serial_numbers.reverse() # reverse list of page Sr number for poping

        data = [{'username': user.username, 
                 'email': user.email, 
                 'last_name': user.last_name, 
                 'first_name': user.first_name, 
                 'id': user.id,
                 'is_active': user.is_active,
                 'serial_number':serial_numbers.pop()
                 } for user in paged_users]
        
        return JsonResponse({'data': data, 'has_previous': paged_users.has_previous(), 
                             'has_next': paged_users.has_next(), 
                             'pages': paginator.num_pages})
    
    ################################### Admin Order Returns ####################################

class AdminReturnsView(View):
    '''
    get method to render return order page.
    post method in this view is used to recieve axios req for
    order return status change to update DB. validate before change status.
    '''
    def get(self, request):
        returns = ReturnOrder.objects.all().order_by('-id')
        paginator = Paginator(returns, 10) 
        page_number = request.GET.get('page')
        try:
            paged_returns = paginator.page(page_number)
        except PageNotAnInteger:
            paged_returns = paginator.page(1)
        except EmptyPage:
            paged_returns = paginator.page(paginator.num_pages)
        # Calculate the starting serial number for the current page
        start_serial_number = (paged_returns.number - 1) * paginator.per_page + 1
        
        # Create a list to hold the serial numbers for the current page
        serial_numbers = list(range(start_serial_number, start_serial_number + len(paged_returns)))
        zipped_data = zip(serial_numbers, paged_returns)

        context = {'zipped_data': zipped_data, 'returns': paged_returns}
        return render(request, 'admin_returns.html', context)
    
    def post(self, request):
        json_data = json.loads(request.body)

        return_id = json_data.get('return_id')
        if return_id:
            new_status = json_data.get('new_status')
            returns = ReturnOrder.objects.get(id=return_id)
            old_status = returns.status
            if old_status == 'D' or old_status == 'R':
                return JsonResponse({
                    'error-msg': 'cannot change Denied or Returned order.',
                    'oldStatus': old_status
                    }, status=400)
            elif new_status == 'P':
                return JsonResponse({
                    'error-msg': 'cannot change back to Pending.',
                    'oldStatus': old_status
                    }, status=400)
            elif new_status == 'S' and old_status == 'R':
                return JsonResponse({
                    'error-msg': 'order already  Recieved.',
                    'oldStatus': old_status
                    }, status=400)
            elif new_status == 'D' and old_status in ['A', 'S']:
                return JsonResponse({
                    'error-msg': 'Cannot reject already approved request.',
                    'oldStatus': old_status
                    }, status=400)
            elif new_status == 'A' and old_status in ['S', 'R']:
                return JsonResponse({
                    'error-msg': 'Request already approved.',
                    'oldStatus': old_status
                    }, status=400)
            elif new_status in ['S', 'R'] and old_status == 'P':
                return JsonResponse({
                    'error-msg': 'Please Approve the request first.',
                    'oldStatus': old_status
                    }, status=400)
            else:
                returns.status = new_status
                returns.save()
                return JsonResponse({'success': True, 'success_msg': 'Order status updated.'})
        else:
            return JsonResponse({'success': False, 'error_msg': 'Order id not found.'})
        
################################### Admin Order Returns Search ####################################

class AdminReturnSearch(View):
    def get(self, request):
        query = request.GET.get('query', '')
        return_status = request.GET.get('returnStatus')
        page_number = request.GET.get('page', 1)
        print(query, return_status, page_number)
        # Filter order list as per status selected 
        if return_status == 'All':
            returns = (
                ReturnOrder.objects
                .filter(Q(order_id__id__icontains=query) | Q(id__icontains=query))
                .order_by('-id')
            )
        else:
            return_status_map = {
                'Pending': 'P',
                'Approved': 'A',
                'Denied': 'D',
                'Shipping': 'S',
                'Received': 'R'
            }
            status = return_status_map.get(return_status)
            returns = (
                ReturnOrder.objects
                .filter(status=status)
                .filter(Q(order_id__id__icontains=query) | Q(id__icontains=query))
                .order_by('-id')
            )
        print(returns)
        # Pagination
        paginator = Paginator(returns, 10)
        try:
            paged_returns = paginator.page(page_number)
        except PageNotAnInteger:
            paged_returns = paginator.page(1)
        except EmptyPage:
            paged_returns = paginator.page(paginator.num_pages)

        # Calculate the starting serial number for the current page
        start_serial_number = (paged_returns.number - 1) * paginator.per_page + 1

        # Create a list to hold the serial numbers for the current page
        serial_numbers = list(range(start_serial_number, start_serial_number + len(paged_returns)))
        serial_numbers.reverse() # reverse list of page Sr number for poping

        data = [{
                'order_id': returns.order_id.id,
                'status': returns.status,
                'id': returns.id,
                'image_1': returns.image_1.url,
                'image_2': returns.image_2.url if returns.image_2 else None,
                'reason': returns.reason,
                'serial_number':serial_numbers.pop()
                } for returns in paged_returns]
        return JsonResponse({'data': data, 'has_previous': paged_returns.has_previous(), 
                             'has_next': paged_returns.has_next(), 
                             'pages': paginator.num_pages})
    
################################### sales report view, download ####################################

class SalesReport(View):
    '''
    Get method to view the sales report.
    Post method to download sales report in excel format using XlsxWriter library.
    '''

    def get(self, request):

        selected_date = request.GET.get('selected_date')
        custom_date_range = request.GET.get('custom_date_range', None)
        
        if selected_date == '7days':
            start_date = datetime.now() - timedelta(days=7)
            end_date = datetime.now()
        elif  selected_date == '30days':
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()
        else:
           if 'to' in custom_date_range:
            start_date_str, end_date_str = custom_date_range.split(' to ')
            date_format = '%Y-%m-%d'
            start_date = datetime.strptime(start_date_str, date_format)
            end_date = datetime.strptime(end_date_str, date_format)
           else:
                start_date_str = end_date_str = custom_date_range
                date_format = '%Y-%m-%d'
                start_date = datetime.strptime(start_date_str, date_format)
                end_date = datetime.strptime(end_date_str, date_format)

        orders = (
            Order.objects
            .filter(add_date__range=[start_date, end_date])
            .order_by('-add_date')
            )
        
        total_price = orders.aggregate(total_price=Sum('price'))['total_price']
        if total_price is not None:
            total_price = f"{total_price:.2f}"
        else:
            total_price = 0.00
        
        paginator = Paginator(orders, 20) 
        page_number = request.GET.get('page')
        try:
            paged_orders = paginator.page(page_number)
        except PageNotAnInteger:
            paged_orders = paginator.page(1)
        except EmptyPage:
            paged_orders = paginator.page(paginator.num_pages)
        # Calculate the starting serial number for the current page
        start_serial_number = (paged_orders.number - 1) * paginator.per_page + 1
        
        # Create a list to hold the serial numbers for the current page
        serial_numbers = list(range(start_serial_number, start_serial_number + len(paged_orders)))
        zipped_data = zip(serial_numbers, paged_orders)

        context = {
            'zipped_data': zipped_data, 
            'orders': paged_orders,
            'total_price': total_price,
            'selected_date': selected_date,
            'custom_date_range': custom_date_range,
            }

        return render(request, 'admin_sales_report.html', context)

    def post(self, request):
        # retrieve selected radio from request
        selected_date = request.POST.get('selected_date')
        # To retrieve date range for custom radio
        custom_date_range = request.POST.get('custom_date_range')
        if selected_date == '7days':
            start_date = datetime.now() - timedelta(days=7)
            end_date = datetime.now()
        elif  selected_date == '30days':
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()
        else:
           if 'to' in custom_date_range:
            start_date_str, end_date_str = custom_date_range.split(' to ')
            date_format = '%Y-%m-%d'
            start_date = datetime.strptime(start_date_str, date_format)
            end_date = datetime.strptime(end_date_str, date_format)
           else:
                start_date_str = end_date_str = custom_date_range
                date_format = '%Y-%m-%d'
                start_date = datetime.strptime(start_date_str, date_format)
                end_date = datetime.strptime(end_date_str, date_format)

        orders = (
            Order.objects
            .filter(add_date__range=[start_date, end_date])
            .order_by('-add_date')
            )
        total_price = orders.aggregate(total_price=Sum('price'))['total_price']
        if total_price is not None:
            total_price = f"{total_price:.2f}"
        else:
            total_price = 0.00

        # Create an in-memory output file for the new workbook.
        output = BytesIO()

        # Create an Excel workbook and add a worksheet.
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # Write the header.
        headers = ['Order ID', 'Product Name', 'Quantity', 'Price', 'Add Date']
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)

        # Write the data.
        row_num = 0
        for row_num, order in enumerate(orders, start=1):
            worksheet.write(row_num, 0, order.id)
            worksheet.write(row_num, 1, order.product_id.name)
            worksheet.write(row_num, 2, float(order.quantity))
            worksheet.write(row_num, 3, float(order.price))
            worksheet.write(row_num, 4, order.add_date.strftime('%d-%m-%Y'))
        bold_right_aligned_format = workbook.add_format({'bold': True, 'align': 'right'})
        worksheet.write(row_num+1, 3, f'Total price: Rs {total_price}', bold_right_aligned_format)

        # Close the workbook.
        workbook.close()

        # Rewind the buffer.
        output.seek(0)

        # For name of the file to be downloaded
        filename_start_date = start_date.strftime('%d%m%Y')
        filename_end_date = end_date.strftime('%d%m%Y')
        filename = f'sales_report_{filename_start_date}_to_{filename_end_date}.xlsx'

        # Set up the response.
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


################################### Banner Section ####################################

class Banner(View):
    '''
    GET method to render the banner page for admin to see banners for
    both men and women langing page.
    '''

    def get(self, request):

        banners_men = BannerMen.objects.all()
        banners_women = BannerWomen.objects.all()
        context = {
            'banners_men': banners_men,
            'banners_women': banners_women,
        }
        return render(request, 'admin_banners.html', context)
    
class BannerEdit(View):
    '''
    GET method to render the banner edit page.
    POST method to update the banner data.
    '''

    def get(self, request):
        id = request.GET.get('banner_id')
        gender = request.GET.get('gender')
        if gender == 'men':
            banner = BannerMen.objects.get(id=id)
        else:
            banner = BannerWomen.objects.get(id=id)
        context = {'banner': banner, 'gender': gender, 'id': id}
        return render(request, 'admin_banner_edit.html', context)
    
    def post(self, request):
        
        id = request.POST.get('id')
        gender = request.POST.get('gender')
        image = request.FILES.get('image')
        caption = request.POST.get('cap')
        caption_colour = request.POST.get('cap_colour')
        errors = []

        if image:
            if image.size > 10 * 1024*1024:
                errors.append('Image size cannot be more than 10mb')
            img_format = imghdr.what(image)
            if not img_format:
                errors.append('Uploaded file is not an image.')
            try:
                img = Image.open(image)
                width, height = img.size
                aspect_ratio = width/height
                print(round(aspect_ratio,2), round(16/9, 2))
                if round(aspect_ratio,2) != round(16/9, 2):
                    errors.append('Images should be with aspect ratio 16:9')
            except Exception as e:
                errors.append('Cannot open the uploaded file.')
        if errors:
            return JsonResponse({'error_msg': errors}, status=400)
        
        if gender == 'men':
            banner = BannerMen.objects.get(id=id)
        else:
            banner = BannerWomen.objects.get(id=id)
            
        if image:
            banner.image = image
            banner.caption= caption
            banner.caption_colour = caption_colour
            banner.save()
        else:
            banner.caption= caption
            banner.caption_colour = caption_colour
            banner.save()

        url = reverse('custom_admin:admin_banners')
        return JsonResponse({'url': url})
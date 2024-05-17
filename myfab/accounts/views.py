from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.generic import View, TemplateView, UpdateView, DeleteView
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LogoutView
from .forms import UserRegistrationForm
from .models import CustomUser, Address
from orders.models import Order
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from .utils import generate_otp, send_otp
from .forms import OTPVerificationForm
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
import re
import json
from .forms import AddressForm


# Create your views here.

############################### Signup CBV ######################################
@method_decorator(never_cache, name='dispatch')
class Signup(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('user:user_home'))
        
        form = UserRegistrationForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            otp = generate_otp()
            send_otp(form.cleaned_data['phone_number'], otp)
            request.session.pop('signup_data', None)   # remove signup, otp data from session before saving new
            request.session.pop('otp', None)
            request.session.pop('expiry_time', None)
            request.session['signup_data'] = form.cleaned_data  # Store form data in session to save after otp verification
            request.session['otp'] = otp                        # Store OTP in session
            expiry_time = datetime.now() + timedelta(minutes=1)
            request.session['expiry_time'] = str(expiry_time)
            return redirect(reverse('accounts:otp_verification')) 
        return render(request, 'signup.html', {'form': form})
    
############################### Login CBV ######################################
@method_decorator(never_cache, name='dispatch')
class LoginPage(TemplateView):

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username = email, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('main:home'))
        else:
            user_exists = CustomUser.objects.filter(username = email).exists()
            context = {'user_exists': user_exists, 'invalid_credentials': True}
            return render(request, 'login.html', context)
        
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('main:home'))
        
        return render(request, 'login.html')

############################### Logout CBV ######################################

class LogoutPage(LogoutView):
    next_page = '/accounts/login/'

    def dispatch(self, request, *args, **kwargs):
       # Delete cookie data
        if request.COOKIES.get('sessionid'):
            request.COOKIES.pop('sessionid')

        # Delete session data
        if request.session:
            request.session.flush()

        return super().dispatch(request, *args, **kwargs)
    
############################### OTP verification CBV ######################################

class OTPVerification(View):
    
    def get(self, request):
        if 'signup_data' not in request.session or 'otp' not in request.session:
            return redirect(reverse('accounts:signup'))
        form = OTPVerificationForm()
        return render(request, 'otp_verification.html', {'form': form})
    
    def post(self, request):
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            stored_otp = request.session.get('otp')
            if entered_otp == stored_otp:            # OTP verification successful, save the user
                expiry_time_str = request.session.get('expiry_time')
                # Remove timezone component before parsing
                expiry_time_str = re.sub(r'\+\d{2}:\d{2}$', '', expiry_time_str)
                expiry_time = datetime.strptime(expiry_time_str, '%Y-%m-%d %H:%M:%S.%f')
                if datetime.now() > expiry_time:
                    context = {'error_otp_expiry':True}
                    return render(request, 'signup.html', context)
                else:
                    form_data = request.session.get('signup_data')
                    form = UserRegistrationForm(form_data)
                    if form.is_valid():
                        form.save()
                        del request.session['signup_data']
                        del request.session['otp']
                        del request.session['expiry_time']
                        return redirect(reverse('accounts:login'))
                    else:
                        return render(request, 'signup.html', {'form': form})
            else:
                context = {'invalid_credentials': True}
                return render(request, 'signup.html', context)
        else:   
            context = {'invalid_credentials': True}
            return render(request, 'signup.html', context)
        
############################### User Profile ######################################

class UserProfile(UpdateView):
    model = CustomUser
    fields = ['first_name', 'last_name']
    template_name = 'profile.html'
    success_url = '/main/'

############################### User Address ######################################
class AddressView(View):
    '''
    To display address page.
    '''
    def get(self, request):
        user = request.user
        addresses = Address.objects.filter(customer_id=user, is_active=True)
        address_count = addresses.count()
        context = {'addresses': addresses, 'address_count': address_count}
        return render(request, 'address.html', context)

############################### User Add Address ######################################
class AddAddress(CreateView):
    '''
    To add new address.
    '''
    model = Address
    form_class = AddressForm
    template_name = 'address_add.html'
    success_url = reverse_lazy('accounts:address')

    

############################### User Delete Address ######################################

def address_delete(request, pk):
    '''
    this view make is_active status of address to False instead of
    deleting an address row. instance of address is referenced by order 
    model which cannot be deleted on cascade.
    '''
    print('address_delete called')
    address = get_object_or_404(Address, pk=pk)

    if request.method == 'POST':
        print(address, address.is_active)
        address.is_active = False
        address.save()
        print(address, address.is_active)
        return redirect(reverse_lazy('accounts:address'))

    

############################### User Address Edit ######################################

class AddressEdit(UpdateView):
    model = Address
    form_class = AddressForm
    template_name = 'address_edit.html'
    success_url = reverse_lazy('accounts:address')


############################### User Orders ######################################

class Orders(View):
    '''
    Get method is To render user orders page.
    Post method is to handle cancel request.
    '''
    def get(self, request):

        user = request.user
        orders = Order.objects.filter(customer_id=user)
        context = {'orders': orders}
        return render(request, 'orders.html', context)
    
    def post(self, request):
        json_data = json.loads(request.body)

        order_id = json_data.get('order_id')
        order = Order.objects.get(id=order_id)
        try:
            order.status = 'C'
            order.save()
        except ValidationError as e:
            print(f'Validation error- {e}')

        return JsonResponse({'success-msg': 'Order cancelled.'})

        

        return JsonResponse({'success': True, 'success-msg': 'Order Cancelled.'})

    
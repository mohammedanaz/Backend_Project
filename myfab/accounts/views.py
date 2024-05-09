from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView, UpdateView
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LogoutView
from .forms import UserRegistrationForm
from .models import CustomUser, Address
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from .utils import generate_otp, send_otp
from .forms import OTPVerificationForm
from datetime import datetime, timedelta
import re



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
        addresses = Address.objects.filter(customer_id=user)
        context = {'addresses': addresses}
        return render(request, 'address.html', context)

############################### User Add Address ######################################
class AddAddress(CreateView):
    '''
    To add new address.
    '''
    model = Address
    fields = ['customer_id', 'name', 'house_name', 'street_name_1',
               'street_name_2', 'city', 'state', 'pincode', 'phone_number']
    template_name = 'address.html'
    success_url = ''


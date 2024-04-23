from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from .forms import UserRegistrationForm
from .models import CustomUser
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

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
            form.save()
            return redirect('login') 
        return render(request, 'signup.html', {'form': form})
    
############################### Login CBV ######################################
@method_decorator(never_cache, name='dispatch')
class LoginPage(TemplateView):

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username = email, password=password)
        print('User is:', user)
        if user is not None:
            login(request, user)
            return redirect(reverse('user:user_home'))
        else:
            user_exists = CustomUser.objects.filter(username = email).exists()
            context = {'user_exists': user_exists, 'invalid_credentials': True}
            return render(request, 'login.html', context)
        
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('user:user_home'))
        
        return render(request, 'login.html')

############################### Login CBV ######################################

class LogoutPage(TemplateView):

    def post(self, request):
        if request.user.is_authenticated:
            logout(request)
        return redirect('accounts:login')
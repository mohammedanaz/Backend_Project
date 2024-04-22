from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from .forms import UserRegistrationForm

# Create your views here.


############################### Signup CBV ######################################
class Signup(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') 
        return render(request, 'signup.html', {'form': form})
    
############################### Login CBV ######################################

class LoginPage(TemplateView):
    template_name = 'login.html'

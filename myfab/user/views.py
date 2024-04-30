from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# Create your views here.

############################### User Home CBV ######################################

@method_decorator(login_required, name='dispatch')
class UserHome(View):
    def get(self, request):
        return render(request, 'user_home.html')
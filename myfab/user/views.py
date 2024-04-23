from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

############################### User Home CBV ######################################

class UserHome(TemplateView):
    template_name = 'user_home.html'
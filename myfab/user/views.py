from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

# Create your views here.

############################### User Home CBV ######################################
@method_decorator(never_cache, name='dispatch')
class UserHome(TemplateView):
    template_name = 'user_home.html'
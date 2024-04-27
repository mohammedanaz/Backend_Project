from django.shortcuts import render
from django.views import View
from .models import Usage

# Create your views here.

############################### Home CBV ######################################

class Home(View):
    def get(self, request, *args, **kwargs):
        usages = Usage.objects.filter(gender='M')  # Filter usages with male gender
        usage_list = list(usages)
        print(usage_list)
        context = {'usages': usage_list}
        return render(request, 'home.html', context)

from django.shortcuts import render
from django.views import View
from .models import Usage, Category, CategoryChoice


# Create your views here.



############################### Home CBV ######################################

class Home(View):
    def get(self, request):
        usages = Usage.objects.filter(gender='M')  # Filter usages with male gender
        usage_list = list(usages)

        categories_without_img = Category.objects.filter(categorychoice__image__isnull=False).distinct()
        categories_filtered = categories_without_img.exclude(name='gender')
        choices_without_img = CategoryChoice.objects.filter(image__isnull=False)
        choices_filtered = choices_without_img.exclude(choices = 'male')
        dict = {}
        for category in categories_filtered:
            choices = choices_filtered.filter(category = category)
            dict[category.name] = choices
        context = {'usages': usage_list,
                   'categories_filtered': categories_filtered,
                   'choices_filtered': choices_filtered,
                   'dict': dict
                   }

        return render(request, 'home.html', context)
    


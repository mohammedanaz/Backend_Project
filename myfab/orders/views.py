from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View

########################## Cart View #################################
class Cart(View):

    def post(self, request):
        product_id = request.POST.get('product_id')

        print('product_id: ', product_id)

        return redirect(reverse('main:products'))
    
    def get(self, request):
        return render(request, 'cart.html')

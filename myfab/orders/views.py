from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from main.models import Product
from django.http import JsonResponse
import json

########################## Cart View #################################
class Cart(View):

    def post(self, request):
        # Parse the JSON data sent from the frontend
        data = json.loads(request.body)

        # Extract relevant fields from the data
        user = request.user
        product_id = data.get('product_id')
        product = Product.objects.get(pk=product_id)
        ordertype = data.get('ordertype')
        dresstype = data.get('dresstype')

        print('product: ', product,
              'user: ', user,
              'ordertype :', ordertype,
              'dresstype :', dresstype
              )

        return JsonResponse({'message': 'Data received successfully'})
    

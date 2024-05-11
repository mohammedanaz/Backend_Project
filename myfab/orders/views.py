from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from main.models import Product
from orders.models import Cart
from django.http import JsonResponse
import json

########################## Cart View #################################
class CartView(View):

    def post(self, request):
        # Parse the JSON data sent from the frontend
        data = json.loads(request.body)
        user = request.user
        product_id = data.get('product_id')
        product = Product.objects.get(pk=product_id)
        ordertype = data.get('ordertype')
        dresstype = data.get('dresstype')
        price = data.get('price')

        # save quantity based on order type
        if int(ordertype) == 1:
            quantity = int(data.get('quantity-FO'))
            cart_item = Cart.objects.create(
                customer_id = user,
                product_id = product,
                order_type = int(ordertype),
                qty = quantity
            )
        else:
            quantity = int(data.get('quantity-FS'))

        print('product: ', product,
              'user: ', user,
              'ordertype :', ordertype,
              'dresstype :', dresstype,
              'price: ', price,
              'quantity: ', quantity
              )

        return JsonResponse({'message': 'Data received successfully'})
    

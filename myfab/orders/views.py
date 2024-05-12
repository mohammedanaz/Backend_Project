from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from main.models import Product, Usage
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
            return JsonResponse({'message': 'Data received successfully'})
        else:
            quantity = int(data.get('quantity-FS'))
            dresstype = Usage.objects.get(name=dresstype)
            measurements_dict = {}
            for measurement in dresstype.measurements.all(  ):
                measurement_name = measurement.name
                measurements_dict[measurement_name] = data.get(measurement_name)

            error_message = 'Cart not saved. Mearurements data processing is pending.'
            return JsonResponse({'error_message': error_message }, status=400)
    

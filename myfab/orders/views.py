from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from main.models import Product, Usage
from accounts.models import Address
from orders.models import Cart
from django.http import JsonResponse
import json
from decimal import Decimal
from accounts.utils import validate_input

########################## Cart View #################################
class CartView(View):

    def post(self, request):
        # Parse the JSON data sent from the frontend(product details page)
        data = json.loads(request.body)
        user = request.user
        product_id = data.get('product_id')
        product = Product.objects.get(pk=product_id)
        ordertype = data.get('ordertype')
        dresstype = data.get('dresstype')
        price = data.get('price')

        # Cart save logics based on order types
        if int(ordertype) == 1:
            quantity = data.get('quantity-FO')
            if validate_input(quantity):
                Cart.objects.create(
                                    customer_id = user,
                                    product_id = product,
                                    order_type = int(ordertype),
                                    qty = Decimal(quantity)
                                    )
                return JsonResponse({'message': 'Cart created successfully.'})
            else:
                error_message = f'Cart not saved. Quantity is not valid.'
                return JsonResponse({'error_message': error_message }, status=400)
            
        
        elif int(ordertype) == 2:
            quantity = data.get('quantity-FS')
            if not validate_input(quantity):
                error_message = f'Cart not saved. Quantity is not valid.'
                return JsonResponse({'error_message': error_message }, status=400)
            dresstype = Usage.objects.get(name=dresstype)
            measurements_dict = {}
            measurements_dict['customer_id'] = user.username
            measurements_dict['dresstype'] = dresstype.name
            for measurement in dresstype.measurements.all():
                measurement_name = measurement.name
                measurement_value = data.get(measurement_name)
                # Check if measurement_value is a valid number
                if validate_input(measurement_value):
                    measurements_dict[measurement_name] = measurement_value
                else:
                    error_message = f'Cart not saved. Measurement {measurement_name} is not valid.'
                    return JsonResponse({'error_message': error_message }, status=400)
            print(measurements_dict, quantity)
            Cart.objects.create(
                                    customer_id = user,
                                    product_id = product,
                                    order_type = int(ordertype),
                                    qty = Decimal(quantity),
                                    cart_measurements = measurements_dict,
                                    )
            return JsonResponse({'message': 'Cart created successfully.'})
        else:
            error_message = 'Cart not saved. Order type not Known.'
            return JsonResponse({'error_message': error_message }, status=400)
    

########################## Checkout View #################################

class CheckoutView(View):
    
    def get(self, request):
        '''
        create address for the user and products from the cart to pass
        to context.
        '''
        user = request.user
        addresses = Address.objects.filter(customer_id=user)
        carts = Cart.objects.filter(customer_id=user)
        subtotal = sum(cart.price for cart in carts)
        grant_total = subtotal + 75
        context = {
            'addresses': addresses,
            'carts': carts,
            'subtotal': subtotal,
            'grant_total': grant_total
            }
        return render(request, 'checkout.html', context)

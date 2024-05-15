from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import UpdateView, DeleteView
from main.models import Product, Usage
from accounts.models import Address
from orders.models import Cart, Order
from django.http import JsonResponse
import json
from decimal import Decimal
from accounts.utils import validate_input
from django.db import transaction, IntegrityError


########################## Cart View #################################
class CartView(View):

    def post(self, request):
        # Parse the JSON data sent from the frontend(product details page)
        data = json.loads(request.body)
        user = request.user
        if user.is_authenticated:
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
        else:
            error_message = 'Login required.'
            return JsonResponse({'error_message': error_message }, status=400)
    

########################## Cart Delete View #################################

class CartDelete(View):
    '''
    To delete cart items with axios.
    '''
    def post(self, request):
        try:
            data = json.loads(request.body)
            cart_id = data.get('cartId')
            Cart.objects.get(id=cart_id).delete()

            # Return success response
            return JsonResponse({'message': 'Cart item deleted successfully.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
########################## Cart Update View #################################
class CartEdit(View):
    
    def post(self, request):
        data = json.loads(request.body)
        new_quantity = data.get('quantity')
        cart_id = data.get('cart_id')
        # Perform Qty validation
        if validate_input(new_quantity):
            cart = Cart.objects.get(id=cart_id)
            cart.qty = Decimal(new_quantity)
            cart.save()
            return JsonResponse({'message': 'Quantity updated successfully'})
        else:
            print('Invalid Qty')
            return JsonResponse({'error': 'Cart item not found'}, status=404)

########################## Create Order View #################################

class CheckoutView(View):
    
    def get(self, request):
        '''
        create address for the user and products from the cart to pass
        to context.
        '''
        # retrieve error msg passed from create order view exception to session data
        insufficient_qty_error_msg = request.session.pop('insufficient_qty_error_msg', None)

        user = request.user
        addresses = Address.objects.filter(customer_id=user, is_active=True)
        carts = Cart.objects.filter(customer_id=user)
        subtotal = sum(cart.price for cart in carts)
        grant_total = subtotal + 75
        context = {
            'addresses': addresses,
            'carts': carts,
            'subtotal': subtotal,
            'grant_total': grant_total,
            'insufficient_qty_error_msg': insufficient_qty_error_msg,
            }
        return render(request, 'checkout.html', context)
    
########################## Create Order View #################################

class CreateOrder(View):

    def post(self, request):
        '''
        using atomic and row locking feature this view will add new rows to 
        order model and delete all the rows of the current user from cart model.
        '''
        user = request.user
        try:
            with transaction.atomic():
                # lock corresponding rows of cart and product to update.
                cart_items = Cart.objects.select_for_update().filter(customer_id=user)
                product_ids = [cart_item.product_id.id for cart_item in cart_items]
                products = Product.objects.select_for_update().filter(id__in=product_ids)
                for cart in cart_items:
                    product = products.get(id=cart.product_id.id)
                    order_type = cart.order_type
                    qty = cart.qty
                    price = cart.price
                    payment_type = request.POST.get('paymentOption')
                    if payment_type == 'COD':
                        payment_method = 'C'
                    else:
                        payment_method = 'P'
                    selected_address = request.POST.get('addressOption')
                    address = Address.objects.get(id=selected_address)
                    order_measurements = cart.cart_measurements

                    if product.qty >= qty + Decimal('0.01'):
                        Order.objects.create(
                            customer_id = user,
                            product_id = product,
                            order_type = order_type,
                            quantity = qty,
                            price = price,
                            payment_method = payment_method,
                            address = address,
                            order_measurements = order_measurements
                        )
                        product.qty -= (qty + Decimal('0.01'))
                        product.save()
                    else:
                        raise Exception(f'Insufficient stock for {product.name}. Only {product.qty}m left.')
                cart_items.delete()
                order_create_msg = 'Your Order Successfully Placed.'
                request.session['order_create_msg'] = order_create_msg
                return redirect(reverse('main:products'))
             
        except IntegrityError:
            print('Integrity error occured')
            return redirect(reverse('orders:checkout'))
        except Exception as e:
            print(f'Exception occured- {e}')
            insufficient_qty_error_msg = f'{e}'
            request.session['insufficient_qty_error_msg'] = insufficient_qty_error_msg
            return redirect(reverse('orders:checkout'))


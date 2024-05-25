from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import UpdateView, DeleteView
from main.models import Product, Usage
from accounts.models import Address, CustomUser
from orders.models import Cart, Order, PaymentOrder, PaymentPrepaid
from django.http import JsonResponse, HttpResponse
import json
from decimal import Decimal
from accounts.utils import validate_input
from django.db import transaction, IntegrityError
from xhtml2pdf import pisa
from django.templatetags.static import static
from django.template.loader import get_template
import razorpay
import hmac
import hashlib
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


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
        addresses = (
            Address.objects
            .filter(customer_id=user, is_active=True)
            .order_by('-id')
            )
        address_count = addresses.count()
        carts = Cart.objects.filter(customer_id=user)
        subtotal = sum(cart.price for cart in carts)
        grant_total = subtotal + 75
        context = {
            'addresses': addresses,
            'carts': carts,
            'subtotal': subtotal,
            'grant_total': grant_total,
            'insufficient_qty_error_msg': insufficient_qty_error_msg,
            'address_count': address_count,
            }
        return render(request, 'checkout.html', context)
    
########################## Create Order View #################################

class CreateOrder(View):

    def post(self, request):
        '''
        for COD payment using atomic and row locking feature this view will add new rows to 
        order model for each cart item and delete all the rows of the current user from 
        cart model.
        for prepaid this will create a payment instance of razorpay and redirects to 
        payment.html with context. and response from razorpay is handled by callback view.
        '''
        user = request.user
        request.session['user_id'] = user.id
        payment_type = request.POST.get('paymentOption')
        if payment_type == 'COD':
            payment_method = 'C'
            try:
                with transaction.atomic():
                    # lock corresponding rows of cart and product to update.
                    cart_items = Cart.objects.select_for_update().filter(customer_id=user)
                    if not cart_items:
                        return redirect(reverse('main:products'))
                    product_ids = [cart_item.product_id.id for cart_item in cart_items]
                    products = Product.objects.select_for_update().filter(id__in=product_ids)


                    for cart in cart_items:
                        product = products.get(id=cart.product_id.id)
                        order_type = cart.order_type
                        qty = cart.qty
                        price = cart.price

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
                    return render(request, 'payment_success.html')
            except IntegrityError:
                print('Integrity error occured')
                return redirect(reverse('orders:checkout'))
            except Exception as e:
                print(f'Exception occured- {e}')
                insufficient_qty_error_msg = f'{e}'
                request.session['insufficient_qty_error_msg'] = insufficient_qty_error_msg
                return redirect(reverse('orders:checkout'))    
        else:
            #Logics for prepaid method
            payment_method = 'P'
            selected_address = request.POST.get('addressOption')
            address = Address.objects.get(id=selected_address)
            try:
                with transaction.atomic():
                    # lock corresponding rows of cart and product to update.
                    cart_items = Cart.objects.select_for_update().filter(customer_id=user)
                    if not cart_items:
                        return redirect(reverse('main:products'))
                    product_ids = [cart_item.product_id.id for cart_item in cart_items]
                    products = Product.objects.select_for_update().filter(id__in=product_ids)

                    total_price = Decimal(0.00)
                    for cart in cart_items:
                        product = products.get(id=cart.product_id.id)
                        order_type = cart.order_type
                        qty = cart.qty
                        price = cart.price

                        selected_address = request.POST.get('addressOption')
                        address = Address.objects.get(id=selected_address)
                        order_measurements = cart.cart_measurements
                        if product.qty >= qty + Decimal('0.01'):
                            total_price += product.price                       
                        else:
                            raise Exception(f'Insufficient stock for {product.name}. Only {product.qty}m left.')

            except IntegrityError:
                print('Integrity error occured')
                return redirect(reverse('orders:checkout'))
            except Exception as e:
                print(f'Exception occured- {e}')
                insufficient_qty_error_msg = f'{e}'
                request.session['insufficient_qty_error_msg'] = insufficient_qty_error_msg
                return redirect(reverse('orders:checkout'))  
            
            #For creating a  Razor Pay client instance
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            order_amount = (total_price+75)*100
            order_currency = 'INR'
            order_receipt = 'order_rcptid_11'
            address_id = address.id

            # Create the Razorpay order
            order = client.order.create({
                'amount': float(order_amount),
                'currency': order_currency,
                'receipt': order_receipt,
                'payment_capture': '1',
            })
            print('************')
            print(order)
            print('************')

            #Create an instance of payment Order model
            order_id = order['id']
            PaymentOrder.objects.create(
                payment_order_id = order_id,
                user_id = user.id,
                address_id = address_id,
                amount = order_amount
            )

            # Prepare the context for payment.html
            context = {
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'order_id': order_id,
                'amount': order_amount,
                'currency': order_currency,
                 'address_id': address_id,
            }
            return render(request, 'payment.html', context)
        
################### view for razorpay webhook for success, failure pay ######################
@method_decorator(csrf_exempt, name='dispatch')
class RazorWebhook(View):

    '''
    To test a response from razorpay webhook. and authenticate
    payment details like paid amount, signature.
    '''

    def post(self, request):
        try:
            print ('Entered inside webhook post req.')
            webhook_secret_key = settings.RAZORPAY_WEBHOOK_SECRET
            received_data = json.loads(request.body)
            received_signature = request.headers.get('X-Razorpay-Signature')

            generated_signature = hmac.new(
                webhook_secret_key.encode('utf-8'),
                request.body,
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(received_signature, generated_signature):
                print('Signature mismatch order not created')
                raise KeyError('Signature keys mismatch. Response tampered.')
            payment_id = received_data['payload']['payment']['entity']['id']
            order_id = received_data['payload']['payment']['entity']['order_id']
            amount = received_data['payload']['payment']['entity']['amount']
            #Retreive the paymentOrder instance from webhook data received.
            payment_order = PaymentOrder.objects.get(payment_order_id=order_id)
            order_amount = payment_order.amount
            #check saved order_amount and amount from webhook similar
            if amount == order_amount:
                user_id = payment_order.user_id
                user = CustomUser.objects.get(id=user_id)
                address_id = payment_order.address_id
                address = Address.objects.get(id=address_id)

                # Atomic block for creating order instance.
                with transaction.atomic():
                    print('Inside atomic transaction')
                    payment_method = 'P'
                    #Create an instance of PaymentPrepaid, Order field will be added to it after
                    # creating each related order model below.
                    payment_prepaid = PaymentPrepaid.objects.create(
                        payment_id = payment_id,
                        amount = order_amount/100 # convert from paisa to rupee
                    )
                    # lock corresponding rows of cart and product to update.
                    cart_items = Cart.objects.select_for_update().filter(customer_id=user)
                    if not cart_items:
                        print('##### No cart  items found #######')
                        raise RuntimeError('Cart items deleted before creating order instances.')
                    product_ids = [cart_item.product_id.id for cart_item in cart_items]
                    products = Product.objects.select_for_update().filter(id__in=product_ids)

                    for cart in cart_items:
                        product = products.get(id=cart.product_id.id)
                        order_type = cart.order_type
                        qty = cart.qty
                        price = cart.price

                        order_measurements = cart.cart_measurements
                        order = Order.objects.create(
                            customer_id = user,
                            product_id = product,
                            order_type = order_type,
                            quantity = qty,
                            price = price,
                            payment_method = payment_method,
                            address = address,
                            order_measurements = order_measurements
                        )
                        payment_prepaid.orders.add(order) #add this order to payment model
                        product.qty -= (qty + Decimal('0.01'))
                        product.save()
                    cart_items.delete()
                    payment_order.delete()
                    return JsonResponse({'success':'success'})
            else:
                print('Exception: Amount paid and order amount mismatch.')
                raise ValueError('Amount paid and order amount mismatch.')
            
        except KeyError as e:
            print('Exception: Key error')
            payment_order.delete()
            error_msg = f'{e}'
            return JsonResponse({'error':'Exception: Key error'}, status=400)
        except ValueError as e:
            print('Exception: Value error')
            payment_order.delete()
            error_msg = f'{e}'
            return JsonResponse({'error':'Exception: Value error'}, status=400)
        except RuntimeError as e:
            print('Exception: Runtime error')
            payment_order.delete()
            error_msg = f'{e}'
            return JsonResponse({'error':'Exception: Runtime error'}, status=400)
        except Exception as e:
            print('Exception: General')
            payment_order.delete()
            error_msg = f'{e}'
            return JsonResponse({'error':'Exception: General'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class PaymentCallback(View):
    '''
    The handler function from front end sends a fetch request to check 
    a payment instance already made by webhook backend logic with 
    the payment_id in the payload. if payment instance exists then its 
    a successfull payment or return error.
    '''
    def post(self, request):
        try:
            print('inside callback method')
            payload = json.loads(request.body)
            if not payload:
                print('Payload is None')
                raise Exception('Payload None')
            payment_id = payload['razorpay_payment_id']
            if not payment_id:
                print('Payment id not found in payload')
                raise ValueError('Payment id not found in payload')
            if PaymentPrepaid.objects.filter(payment_id=payment_id).exists():
                return JsonResponse({'success': 'Payment id found'})
            else:
                return JsonResponse({'error': 'Payment id not found'},status=500)
        except ValueError as e:
            return JsonResponse({'error': e}, status=400)
        except Exception as e:
            return JsonResponse({'error': e}, status=400)



########################## Payment Succes, Failure pages #################################
class PaymentSuccess(View):
    '''
    To render payment success page after payment verification and order model creation
    from webhook view.
    '''
    def get(self, request):
        return render(request, 'payment_success.html')

class PaymentFailed(View):
    '''
    To render payment failed page after payment verification failed
    from webhook view.
    '''
    def get(self, request):
        return render(request, 'payment_failed.html')

########################## Create Invoice View #################################

class Invoice(View):
    '''
    To render invoice and download.
    '''

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        total = order.price + 75
        context = {
            'order': order,
            'total': total,
        }
        return render(request, 'invoice.html', context)
    
########################## Generate Invoice pdf View #################################
    
def generate_invoice_pdf(request, pk):
    order = get_object_or_404(Order, pk=pk)
    total = order.price + 75
    template = get_template('invoice_pdf.html')
    context = {'order': order, 'total': total}
    logo_url = request.build_absolute_uri(static('images/MyFAB_logo_for_pdf.png'))
    html_content = template.render({'order': order, 'total': total, 'logo_url': logo_url})
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
    
    pisa_status = pisa.CreatePDF(html_content, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html_content + '</pre>')
    
    return response
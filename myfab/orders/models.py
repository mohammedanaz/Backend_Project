from django.db import models
from main.models import Product
from accounts.models import Address, CustomUser
from decimal import Decimal, ROUND_HALF_UP
import json
from django.core.exceptions import ValidationError

class Cart(models.Model):
    '''
    details of cart will be stored here. when user makes order of this
    cart, those cart items will be removed from this model. Measurements details are
    stored as dictionary in the cart to pass to stitching measurements model when 
    order proceeds. Json validations are applied while serializing and deserializing.
    '''
    customer_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_type = models.IntegerField(null=False)
    qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cart_measurements = models.TextField(null=True, default=None, blank=True)

    def set_cart_measurements(self, value):
        try:
            json_data = json.dumps(value)
            self.cart_measurements = json_data
        except (TypeError, ValueError):
            raise ValidationError("Invalid JSON data")

    def get_cart_measurements(self):
        try:
            json_data = json.loads(self.cart_measurements)
            return json_data
        except json.JSONDecodeError:
            return None

    def save(self, *args, **kwargs):
        '''
        cart price is rounded to 2 decimal after multiplying unit price with quantity.
        '''
        if self.product_id:
            # Round the price to 2 decimal places
            self.price = Decimal(self.qty * self.product_id.price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)

    
class Order(models.Model):
    '''
    information about each order will be saved here. 
    it will have 4 status (pending, shipping, delivered, cancelled).
    2 payment method(prepaid, COD)
    '''
    PAYMENT_CHOICES = [
        ('P', 'Prepaid'),
        ('C', 'Cash On Delivery'),
    ]

    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('S', 'Shipping'),
        ('D', 'Delivered'),
        ('C', 'Cancelled'),
        ('R', 'Returned'),
    ]

    customer_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_type = models.IntegerField(null=False)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    add_date = models.DateField(auto_now_add=True)
    payment_method = models.CharField(max_length=10, null=False, choices=PAYMENT_CHOICES)
    status = models.CharField(max_length=10, null=False, choices=STATUS_CHOICES, default='P')
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    order_measurements = models.TextField(null=True, default=None, blank=True)


    def __str__(self):
        return f"{self.pk}, {self.customer_id}"
    
    def set_order_measurements(self, value):
        try:
            json_data = json.dumps(value)
            self.order_measurements = json_data
        except (TypeError, ValueError):
            raise ValidationError("Invalid JSON data")

    def get_order_measurements(self):
        try:
            json_data = json.loads(self.order_measurements)
            return json_data
        except json.JSONDecodeError:
            return None
    

class ReturnOrder(models.Model):
    '''
    To store return request datas.
    '''

    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('D', 'Denied'),
        ('S', 'Shipping'),
        ('R', 'Received'),
    ]
    
    order_id = models.ForeignKey(Order, on_delete=models.PROTECT)
    reason = models.TextField(null=False, blank=False)
    image_1 = models.ImageField(upload_to='images/return_order', null=False, blank=False)
    image_2 = models.ImageField(upload_to='images/return_order', null=True, blank=True)
    status = models.CharField(max_length=10, null=False, choices=STATUS_CHOICES, default='P')

class PaymentOrder(models.Model):
    '''
    to create a temperory model to store the payment instance created by 
    razorpay for processing payment. this datas will be used while payment 
    verification and then creating an order and payment instance.
    '''
    payment_order_id = models.TextField(null=False, blank=True)
    user_id = models.CharField(max_length=250, null=False, blank=True)
    address_id = models.CharField(max_length=250, null=False, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    
class PaymentPrepaid(models.Model):
    '''
    Here the payment details for prepaid are stored after successful
    payment verification. payment_id will be id got from payment service provider.
    '''
    payment_id = models.TextField(null=False, blank=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    orders = models.ManyToManyField(Order, blank=True)

class PaymentCOD(models.Model):
    '''
    Here the payment amount and order of COD type will be stored when the 
    order status goes to delivered.
    '''
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
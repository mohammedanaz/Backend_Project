from django.db import models
from main.models import Product
from accounts.models import CustomUser
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
    cart_measurements = models.TextField(null=True)

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
    ]

    customer_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_type = models.IntegerField(null=False)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    add_date = models.DateField(auto_now_add=True)
    payment_method = models.CharField(max_length=10, null=False, choices=PAYMENT_CHOICES)
    status = models.CharField(max_length=10, null=False, choices=STATUS_CHOICES, default='P')
    order_measurements = models.TextField(null=True)


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
    


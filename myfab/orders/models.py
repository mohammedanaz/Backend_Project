from django.db import models
from main.models import Product
from accounts.models import CustomUser
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError

class Cart(models.Model):
    '''
    details of cart will be stored here. when user makes order of this
    cart, those cart items will be removed from this model. 
    '''
    customer_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_type = models.IntegerField(null=False)
    qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        '''
        cart price is rounded to 2 decimal after multiplying unit price with quantity.
        '''
        if self.product_id:
            # Round the price to 2 decimal places
            self.price = Decimal(self.qty * self.product_id.price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)


class Address(models.Model):
    '''
    Address of each customer and guest will be saves here. name and phone_number 
    will be a unique combination.
    '''
    customer_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=False, null=False)
    house_name = models.CharField(max_length=100, blank=False, null=False)
    street_name_1 = models.CharField(max_length=100, blank=False, null=False)
    street_name_2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=False, null=False)
    state = models.CharField(max_length=100, blank=False, null=False)
    pincode = models.CharField(max_length=10, blank=False, null=False)
    phone_number = models.CharField(max_length=13)

    def clean(self):
        # Ensure that the combination of name and phone_number is unique
        if Address.objects.filter(name=self.name, phone_number=self.phone_number).exists():
            raise ValidationError("An address with this name and phone number already exists.")
        super().clean()

    def __str__(self):
        return f"{self.name}, {self.house_name}"
    
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
    status = models.CharField(max_length=10, null=False, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.pk}, {self.customer_id}"
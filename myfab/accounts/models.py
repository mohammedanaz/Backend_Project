from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# Create your models here.

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=13, unique=True)



    
class Address(models.Model):
    '''
    Address of each customer and guest will be saves here. name and phone_number 
    will be a unique combination for each customer.
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
    is_active = models.BooleanField(default=True)

    def clean(self):
        # Ensure that the combination of pincode, phone_number, and customer_id is unique
        existing_addresses = Address.objects.filter(
            pincode=self.pincode,
            phone_number=self.phone_number,
            customer_id=self.customer_id
        ).exclude(is_active=False).exclude(pk=self.pk)  # Exclude the current instance being edited
        if existing_addresses.exists():
            raise ValidationError("An address with this pincode, phone number already exists for this customer.")
        super().clean()

    def __str__(self):
        return f"{self.customer_id}, {self.name}, {self.house_name}"
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
        if Address.objects.filter(pincode=self.pincode, phone_number=self.phone_number, customer_id=self.customer_id).exists():
            print('same name, phone# exixsts')
            raise ValidationError("An address with this pincode and phone number already exists for this customer.")
        super().clean()

    def __str__(self):
        return f"{self.customer_id}, {self.name}, {self.house_name}"
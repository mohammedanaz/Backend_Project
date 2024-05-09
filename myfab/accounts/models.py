from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# Create your models here.

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=13, unique=True)

    def __str__(self):
         return self.first_name if self.first_name else self.username

    
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
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# Create your models here.

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=13, unique=True)


    
    def __str__(self):

         return self.first_name if self.first_name else self.username

    

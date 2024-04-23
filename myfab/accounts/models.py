from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# Create your models here.

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=13, unique=True)

#################### new reverse relation names for ORM ##############
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        related_query_name='user_group'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        related_query_name='user_permission'
    )
    
    def __str__(self):
        return self.first_name
    

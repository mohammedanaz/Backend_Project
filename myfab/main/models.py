from django.core.validators import MinValueValidator
from django.db import models

class Usage(models.Model):
    '''
    model to provide possible usage types
    '''
    GENDER_CHOICES = [
        ('M', 'male'),
        ('F', 'female'),
    ]
    name = models.CharField(max_length=100, null=False, unique=True)
    image = models.ImageField(upload_to='images/usages', null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, choices=GENDER_CHOICES)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class CategoryChoice(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='images/category_choices', null=True, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='images/products')
    description = models.TextField(blank=True)
    qty = models.FloatField(default=0, validators=[MinValueValidator(0)])
    add_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    usages = models.ManyToManyField(Usage)
    category_choices = models.ManyToManyField(CategoryChoice)

    def __str__(self):
        return self.name

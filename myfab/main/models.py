from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.

class Usage(models.Model):
    '''
    model to provide possible usage types
    '''
    name = models.CharField(max_length=100, null=False, unique=True)

    def __str__(self):
        return self.name
    

class Product(models.Model):
        
        GENDER_CHOICES = [
            ('M', 'Male'),
            ('F', 'Female'),
            ('U', 'Unisex')
        ]
        
        MATERIAL_CHOICES = [
            ('Cotton', 'Cotton'),
            ('Polyester', 'Polyester'),
            ('Leather', 'Leather'),
            ('Silk', 'Silk'),
            ('Wool', 'Wool'),
            ('Linen', 'Linen'),
            ('Nylon', 'Nylon'),
            ('Rayon', 'Rayon'),
            ('Other', 'Other')
        ]
        
        PATTERN_CHOICES = [
            ('Solid', 'Solid'),
            ('Striped', 'Striped'),
            ('Floral', 'Floral'),
            ('Checkered', 'Checkered'),
            ('Abstract', 'Abstract'),
            ('Other', 'Other')
        ]
        
        COLOUR_CHOICES = [
            ('Red', 'Red'),
            ('Blue', 'Blue'),
            ('Green', 'Green'),
            ('Yellow', 'Yellow'),
            ('Black', 'Black'),
            ('White', 'White'),
            ('Other', 'Other')
        ]
        
        TEXTURE_CHOICES = [
            ('Knit', 'Knit'),
            ('Woven', 'Woven'),
            ('Denim', 'Denim'),
            ('Velvet', 'Velvet'),
            ('Silky', 'Silky'),
            ('Other', 'Other')
        ]

        name = models.CharField(max_length=255, null=False, blank=False)
        price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
        )
        image = models.ImageField(upload_to='product_images/')
        description = models.TextField(blank=True)
        qty = models.FloatField(default=0, validators=[MinValueValidator(0)])
        add_date = models.DateField(auto_now_add=True)
        stock_count = models.BigIntegerField(default=0, validators=[MinValueValidator(0)])
        is_active = models.BooleanField(default=True)
        gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
        material = models.CharField(max_length=20, choices=MATERIAL_CHOICES)
        pattern = models.CharField(max_length=20, choices=PATTERN_CHOICES)
        colour = models.CharField(max_length=20, choices=COLOUR_CHOICES)
        texture = models.CharField(max_length=20, choices=TEXTURE_CHOICES)
        usages = models.ManyToManyField(Usage)

        def __str__(self):
            return self.name
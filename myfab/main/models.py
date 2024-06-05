from django.core.validators import MinValueValidator
from django.db import models
from django.core.cache import cache

class Measurement(models.Model):
    '''
    model to provide possible measurements to each dress type.
    '''
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Usage(models.Model):
    '''
    model to provide possible usage types(dress types.)
    '''
    GENDER_CHOICES = [
        ('M', 'male'),
        ('F', 'female'),
    ]
    name = models.CharField(max_length=100, null=False, unique=True)
    image = models.ImageField(upload_to='images/usages', null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, choices=GENDER_CHOICES)
    measurements = models.ManyToManyField(Measurement)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        '''
        override save method to delete cache of 'usage_list' if updation happened on this model
        '''
        super().save(*args, **kwargs) # this ensures that usual save() method of parent also executed
        cache.delete('usage_list_male')
        cache.delete('usage_list_female')
    

class Category(models.Model):
    '''
    Used to store category name.
    '''
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        '''
        override save method to delete cache of 'categories_filtered' if updation happened on this model
        '''
        super().save(*args, **kwargs) # this ensures that usual save() method of parent also executed
        cache.delete('categories_filtered')

class CategoryChoice(models.Model):
    '''
    Used to store choices for each category, this can be chenged my 
    admin in future.
    '''
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='images/category_choices', null=True, blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        '''
        override save method to delete cache of 'choices_filtered' if updation happened on this model
        '''
        super().save(*args, **kwargs) # this ensures that usual save() method of parent also executed
        cache.delete('choices_filtered')
        

class Product(models.Model):
    '''
    Used to store product info.
    '''
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='images/products')
    description = models.TextField(blank=True)
    qty = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    add_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    usages = models.ManyToManyField(Usage)
    category_choices = models.ManyToManyField(CategoryChoice)

    def __str__(self):
        return self.name
    

class BannerMen(models.Model):
    '''
    Used to store img and caption for carousel on men 
    landing page.
    '''
    image = models.ImageField(upload_to='images/banner')
    caption = models.CharField(max_length=100, blank=True, null=True)
    caption_colour = models.CharField(max_length=10, default='#FFFFFF')

    def save(self, *args, **kwargs):
        '''
        override save method to delete cache of 'banners_men' if updation happened on this model
        '''
        super().save(*args, **kwargs) # this ensures that usual save() method of parent also executed
        cache.delete('banners_men')

class BannerWomen(models.Model):
    '''
    Used to store img and caption for carousel on women 
    landing page.
    '''
    image = models.ImageField(upload_to='images/banner')
    caption = models.CharField(max_length=100, blank=True, null=True)
    caption_colour = models.CharField(max_length=10, default='#FFFFFF')

    def save(self, *args, **kwargs):
        '''
        override save method to delete cache of 'banners_women' if updation happened on this model
        '''
        super().save(*args, **kwargs) # this ensures that usual save() method of parent also executed
        cache.delete('banners_female')
from django.db import models
from main.models import Product
from accounts.models import CustomUser
from decimal import Decimal, ROUND_HALF_UP

class Cart(models.Model):
    customer_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_type = models.IntegerField(null=False)
    qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if self.product_id:
            # Round the price to 2 decimal places
            self.price = Decimal(self.qty * self.product_id.price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)
# Generated by Django 5.0.4 on 2024-05-15 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_alter_order_order_measurements'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='cart_measurements',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]

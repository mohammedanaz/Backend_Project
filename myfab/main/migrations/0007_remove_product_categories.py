# Generated by Django 5.0.4 on 2024-05-01 08:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_product_categories_product_category_choices'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='categories',
        ),
    ]

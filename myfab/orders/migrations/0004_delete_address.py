# Generated by Django 5.0.4 on 2024-05-09 16:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_address_customer_id_order'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Address',
        ),
    ]
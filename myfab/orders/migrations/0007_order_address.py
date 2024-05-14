# Generated by Django 5.0.4 on 2024-05-13 06:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_address_is_active'),
        ('orders', '0006_order_order_measurements_alter_order_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='accounts.address'),
        ),
    ]
# Generated by Django 5.0.4 on 2024-05-07 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_usage_measurements'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usage',
            name='measurements',
            field=models.TextField(default='["Measurements to be added"]'),
        ),
    ]

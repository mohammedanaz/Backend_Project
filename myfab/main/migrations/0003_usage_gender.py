# Generated by Django 5.0.4 on 2024-04-27 04:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_usage_image_alter_product_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='usage',
            name='gender',
            field=models.CharField(choices=[('M', 'male'), ('F', 'female')], max_length=10, null=True),
        ),
    ]

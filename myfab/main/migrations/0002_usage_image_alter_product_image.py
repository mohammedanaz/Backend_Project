# Generated by Django 5.0.4 on 2024-04-27 03:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usage',
            name='image',
            field=models.ImageField(null=True, upload_to='images/usages'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(upload_to='images/products'),
        ),
    ]

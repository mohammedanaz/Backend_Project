# Generated by Django 5.0.4 on 2024-04-27 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_usage_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='categorychoice',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/usage_choices'),
        ),
        migrations.AlterField(
            model_name='usage',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/usages'),
        ),
    ]

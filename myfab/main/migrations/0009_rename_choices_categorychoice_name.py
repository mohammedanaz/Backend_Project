# Generated by Django 5.0.4 on 2024-05-02 02:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_alter_product_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='categorychoice',
            old_name='choices',
            new_name='name',
        ),
    ]

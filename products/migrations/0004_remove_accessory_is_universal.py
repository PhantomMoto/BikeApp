# Generated by Django 5.2.3 on 2025-06-22 05:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_accessory_is_universal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accessory',
            name='is_universal',
        ),
    ]

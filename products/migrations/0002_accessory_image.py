# Generated by Django 5.2.3 on 2025-06-22 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='accessory',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='accessories/'),
        ),
    ]

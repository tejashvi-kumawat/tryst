# Generated by Django 5.0.1 on 2024-03-12 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accommodation', '0002_remove_accommodation_paymentproof'),
    ]

    operations = [
        migrations.AddField(
            model_name='accommodation',
            name='amount',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

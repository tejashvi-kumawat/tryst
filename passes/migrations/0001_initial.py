# Generated by Django 5.0.1 on 2024-02-05 06:36

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userId', models.CharField(max_length=100)),
                ('slotId', models.CharField(max_length=100)),
                ('code', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('entry', models.BooleanField(default=False)),
                ('entryTime', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pronite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Slot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proniteId', models.CharField(max_length=100)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('capacity', models.IntegerField()),
                ('category', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='TeamPass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teamId', models.CharField(max_length=100)),
                ('slotId', models.CharField(max_length=100)),
                ('code', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('entry', models.BooleanField(default=True)),
                ('entryTime', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Wize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emailId', models.CharField(max_length=100)),
                ('qrId', models.CharField(max_length=100)),
                ('eventId', models.CharField(max_length=100)),
            ],
        ),
    ]

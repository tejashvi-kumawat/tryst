# Generated by Django 5.0.1 on 2024-02-12 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_rename_team_number_pac_teamname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pac',
            name='teamName',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]

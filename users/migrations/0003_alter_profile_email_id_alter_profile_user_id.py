from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_rename_categoty_pac_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='email_ID',
            field=models.EmailField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user_ID',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]

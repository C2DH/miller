# Generated by Django 3.0.6 on 2020-05-26 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miller', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

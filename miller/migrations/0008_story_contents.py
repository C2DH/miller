# Generated by Django 3.0.7 on 2020-06-08 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miller', '0007_auto_20200608_1814'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='contents',
            field=models.TextField(blank=True, default='', verbose_name='mardown content'),
        ),
    ]
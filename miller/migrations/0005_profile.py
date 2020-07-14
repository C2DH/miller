# Generated by Django 3.0.7 on 2020-06-05 14:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import miller.utils.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('miller', '0004_auto_20200605_1045'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_url', models.CharField(default=miller.utils.models.create_short_url, max_length=22, unique=True)),
                ('bio', models.TextField(blank=True, null=True)),
                ('picture', models.URLField(blank=True, max_length=160, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_last_modified', models.DateTimeField(auto_now=True)),
                ('date_last_notified', models.DateTimeField(auto_now_add=True)),
                ('newsletter', models.CharField(choices=[('W', 'weekly'), ('M', 'monthly'), ('0', 'never')], default='W', max_length=1)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
# Generated by Django 3.0.7 on 2020-06-05 10:45

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('miller', '0003_auto_20200604_0853'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='document',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_vector'], name='miller_docu_search__5dead7_gin'),
        ),
    ]

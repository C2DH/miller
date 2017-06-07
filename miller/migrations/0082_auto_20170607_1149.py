# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-07 11:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miller', '0081_remove_tag_metadata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='metadata',
            field=models.TextField(blank=True, default=b'{\n "abstract": {\n  "de_DE": "", \n  "en_US": "", \n  "fr_FR": ""\n }, \n "title": {\n  "de_DE": "", \n  "en_US": "", \n  "fr_FR": ""\n }\n}'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together=set([('name', 'category')]),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-09-06 16:07
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('miller', '0019_tag_metadata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='metadata',
            field=jsonfield.fields.JSONField(default=b'{"name": {}}'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-09-06 15:29
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('miller', '0018_auto_20160902_0908'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='metadata',
            field=jsonfield.fields.JSONField(default=b'{"name": {"en_US": "", "fr_FR": ""}}'),
        ),
    ]
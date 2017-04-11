# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-04-11 09:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miller', '0068_auto_20170407_1348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='category',
            field=models.CharField(choices=[(b'editing', b'editing'), (b'double', b'double blind'), (b'closing', b'closing remarks')], default=b'editing', max_length=8),
        ),
        migrations.AlterField(
            model_name='story',
            name='status',
            field=models.CharField(choices=[(b'draft', b'draft'), (b'shared', b'shared'), (b'public', b'public'), (b'deleted', b'deleted'), (b'pending', b'pending review'), (b'editing', b'editing'), (b'review', b'review'), (b'reviewdone', b'review done')], db_index=True, default=b'draft', max_length=10),
        ),
    ]

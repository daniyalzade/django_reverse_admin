# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'created_at'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='address',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name=b'updated_at'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'created_at'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name=b'updated_at'),
            preserve_default=True,
        ),
    ]

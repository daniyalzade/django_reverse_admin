# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_auto_20180908_1710'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='address',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='person',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='person',
            name='updated_at',
        ),
    ]

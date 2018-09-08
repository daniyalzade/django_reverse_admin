# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name=b'created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name=b'updated at')),
                ('street', models.CharField(max_length=255)),
                ('street_2', models.CharField(max_length=255, null=True, blank=True)),
                ('zipcode', models.CharField(max_length=10)),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=2)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name=b'created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name=b'updated at')),
                ('name', models.CharField(max_length=255)),
                ('home_addr', models.OneToOneField(related_name='person', null=True, blank=True, to='polls.Address')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NonInlinePerson',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('polls.person',),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-15 09:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20170415_0952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='savedurl',
            name='url',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Url'),
        ),
    ]

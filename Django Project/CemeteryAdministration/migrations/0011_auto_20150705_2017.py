# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('CemeteryAdministration', '0010_auto_20150705_2011'),
    ]

    operations = [
        migrations.AddField(
            model_name='operation',
            name='data',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='nryear',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='operation',
            name='type',
            field=models.CharField(default='bral', max_length=4, choices=[('bral', 'inhumare'), ('exhm', 'dezhumare')]),
        ),
    ]

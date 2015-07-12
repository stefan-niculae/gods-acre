# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CemeteryAdministration', '0017_auto_20150712_1423'),
    ]

    operations = [
        migrations.AddField(
            model_name='owner',
            name='phone',
            field=models.CharField(blank=True, null=True, max_length=15),
        ),
        migrations.AddField(
            model_name='spot',
            name='note',
            field=models.CharField(blank=True, null=True, max_length=250),
        ),
    ]

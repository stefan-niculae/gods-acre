# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CemeteryAdministration', '0011_auto_20150705_2017'),
    ]

    operations = [
        migrations.RenameField(
            model_name='operation',
            old_name='data',
            new_name='date',
        ),
        migrations.AlterField(
            model_name='operation',
            name='note',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CemeteryAdministration', '0009_owner_ownership_deed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='operation',
            name='notes',
        ),
        migrations.AddField(
            model_name='operation',
            name='note',
            field=models.CharField(null=True, max_length=250),
        ),
    ]

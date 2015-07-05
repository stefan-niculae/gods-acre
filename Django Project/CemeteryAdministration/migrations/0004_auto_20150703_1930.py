# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CemeteryAdministration', '0003_auto_20150703_1915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nryear',
            name='date',
            field=models.DateField(),
        ),
    ]

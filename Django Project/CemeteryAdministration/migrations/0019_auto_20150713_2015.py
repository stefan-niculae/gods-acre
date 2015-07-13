# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CemeteryAdministration', '0018_auto_20150712_1425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operation',
            name='spot',
            field=models.ForeignKey(related_name='operations', to='CemeteryAdministration.Spot'),
        ),
    ]

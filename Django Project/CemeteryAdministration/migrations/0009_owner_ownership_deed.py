# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CemeteryAdministration', '0008_auto_20150705_1021'),
    ]

    operations = [
        migrations.AddField(
            model_name='owner',
            name='ownership_deed',
            field=models.ForeignKey(default=1, to='CemeteryAdministration.OwnershipDeed'),
            preserve_default=False,
        ),
    ]

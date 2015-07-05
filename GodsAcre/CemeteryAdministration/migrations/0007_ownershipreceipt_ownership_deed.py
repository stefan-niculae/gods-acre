# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CemeteryAdministration', '0006_auto_20150705_0839'),
    ]

    operations = [
        migrations.AddField(
            model_name='ownershipreceipt',
            name='ownership_deed',
            field=models.ForeignKey(default=1, to='CemeteryAdministration.OwnershipDeed'),
            preserve_default=False,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CemeteryAdministration', '0015_auto_20150709_1805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ownershipreceipt',
            name='ownership_deed',
            field=models.ForeignKey(related_name='receipts', to='CemeteryAdministration.OwnershipDeed'),
        ),
    ]

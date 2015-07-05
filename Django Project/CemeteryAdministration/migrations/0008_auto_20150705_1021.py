# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CemeteryAdministration', '0007_ownershipreceipt_ownership_deed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ownershipdeed',
            name='spots',
            field=models.ManyToManyField(related_name='ownership_deeds', to='CemeteryAdministration.Spot'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CemeteryAdministration', '0014_auto_20150706_2131'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='owner',
            name='ownership_deed',
        ),
        migrations.AddField(
            model_name='owner',
            name='ownership_deeds',
            field=models.ManyToManyField(related_name='owners', to='CemeteryAdministration.OwnershipDeed'),
        ),
        migrations.AlterField(
            model_name='ownershipreceipt',
            name='ownership_deed',
            field=models.OneToOneField(related_name='receipt', to='CemeteryAdministration.OwnershipDeed'),
        ),
    ]

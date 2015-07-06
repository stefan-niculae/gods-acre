# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CemeteryAdministration', '0013_construction_construction_authorization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='construction',
            name='construction_authorization',
            field=models.ForeignKey(related_name='constructions', to='CemeteryAdministration.ConstructionAuthorization'),
        ),
        migrations.AlterField(
            model_name='construction',
            name='construction_company',
            field=models.ForeignKey(to='CemeteryAdministration.ConstructionCompany', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='construction',
            name='owner_builder',
            field=models.ForeignKey(to='CemeteryAdministration.Owner', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='construction',
            name='type',
            field=models.CharField(default='brdr', choices=[('brdr', 'bordură'), ('tomb', 'cavou')], max_length=4),
        ),
        migrations.AlterField(
            model_name='maintenancelevel',
            name='description',
            field=models.CharField(default='kept', choices=[('kept', 'întreținut'), ('ukpt', 'neîntreținut')], max_length=4),
        ),
        migrations.AlterField(
            model_name='operation',
            name='type',
            field=models.CharField(default='bral', choices=[('bral', 'înhumare'), ('exhm', 'dezhumare')], max_length=4),
        ),
        migrations.AlterField(
            model_name='ownershipreceipt',
            name='ownership_deed',
            field=models.OneToOneField(to='CemeteryAdministration.OwnershipDeed'),
        ),
    ]

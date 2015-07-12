# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CemeteryAdministration', '0016_auto_20150710_2043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='constructionauthorization',
            name='spots',
            field=models.ManyToManyField(related_name='construction_authorizations', to='CemeteryAdministration.Spot'),
        ),
    ]

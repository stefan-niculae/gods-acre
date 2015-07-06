# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CemeteryAdministration', '0012_auto_20150705_2026'),
    ]

    operations = [
        migrations.AddField(
            model_name='construction',
            name='construction_authorization',
            field=models.ForeignKey(default=1, to='CemeteryAdministration.ConstructionAuthorization'),
            preserve_default=False,
        ),
    ]

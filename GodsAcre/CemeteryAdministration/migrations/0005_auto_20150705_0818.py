# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CemeteryAdministration', '0004_auto_20150703_1930'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='maintenencelevel',
            unique_together=set([('spot', 'year')]),
        ),
    ]

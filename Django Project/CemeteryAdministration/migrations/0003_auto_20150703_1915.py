# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('CemeteryAdministration', '0002_auto_20150703_1909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nryear',
            name='date',
            field=models.DateField(default=datetime.datetime(2015, 7, 3, 19, 15, 43, 639163, tzinfo=utc)),
        ),
    ]

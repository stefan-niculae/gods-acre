# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CemeteryAdministration', '0005_auto_20150705_0818'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaintenanceLevel',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('year', models.IntegerField()),
                ('description', models.CharField(default='kept', choices=[('kept', 'intretinut'), ('ukpt', 'neintretinut')], max_length=4)),
                ('spot', models.ForeignKey(to='CemeteryAdministration.Spot')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='maintenencelevel',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='maintenencelevel',
            name='spot',
        ),
        migrations.DeleteModel(
            name='MaintenenceLevel',
        ),
        migrations.AlterUniqueTogether(
            name='maintenancelevel',
            unique_together=set([('spot', 'year')]),
        ),
    ]

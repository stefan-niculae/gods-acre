# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Concesiune',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('numar', models.IntegerField()),
                ('data', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Loc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('parcela', models.CharField(max_length=10)),
                ('rand', models.CharField(max_length=10)),
                ('coloana', models.CharField(max_length=10)),
            ],
        ),
        migrations.AddField(
            model_name='concesiune',
            name='locuri',
            field=models.ManyToManyField(to='CemeteryAdministration.Loc'),
        ),
    ]

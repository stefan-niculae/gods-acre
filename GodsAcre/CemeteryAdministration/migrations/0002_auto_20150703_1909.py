# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('CemeteryAdministration', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Construction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('type', models.CharField(max_length=4, default='brdr', choices=[('brdr', 'bordura'), ('tomb', 'cavou')])),
            ],
        ),
        migrations.CreateModel(
            name='ConstructionCompany',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='MaintenenceLevel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('year', models.IntegerField()),
                ('description', models.CharField(max_length=4, default='kept', choices=[('kept', 'intretinut'), ('ukpt', 'neintretinut')])),
            ],
        ),
        migrations.CreateModel(
            name='NrYear',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('number', models.IntegerField()),
                ('date', models.DateField(default=datetime.datetime(2015, 7, 3, 19, 8, 31, 814695, tzinfo=utc))),
            ],
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('type', models.CharField(max_length=4, default='bral', choices=[('bral', 'bordura'), ('exhm', 'cavou')])),
                ('first_name', models.CharField(max_length=25)),
                ('last_name', models.CharField(max_length=25)),
                ('notes', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('first_name', models.CharField(max_length=25)),
                ('last_name', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='YearlyPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('year', models.IntegerField()),
                ('value', models.IntegerField()),
            ],
        ),
        migrations.RenameModel(
            old_name='Loc',
            new_name='Spot',
        ),
        migrations.RemoveField(
            model_name='concesiune',
            name='locuri',
        ),
        migrations.RenameField(
            model_name='spot',
            old_name='coloana',
            new_name='column',
        ),
        migrations.RenameField(
            model_name='spot',
            old_name='parcela',
            new_name='parcel',
        ),
        migrations.RenameField(
            model_name='spot',
            old_name='rand',
            new_name='row',
        ),
        migrations.CreateModel(
            name='ConstructionAuthorization',
            fields=[
                ('nryear_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='CemeteryAdministration.NrYear', serialize=False, parent_link=True)),
                ('spots', models.ManyToManyField(to='CemeteryAdministration.Spot')),
            ],
            bases=('CemeteryAdministration.nryear',),
        ),
        migrations.CreateModel(
            name='ContributionReceipt',
            fields=[
                ('nryear_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='CemeteryAdministration.NrYear', serialize=False, parent_link=True)),
            ],
            bases=('CemeteryAdministration.nryear',),
        ),
        migrations.CreateModel(
            name='OwnershipDeed',
            fields=[
                ('nryear_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='CemeteryAdministration.NrYear', serialize=False, parent_link=True)),
                ('spots', models.ManyToManyField(to='CemeteryAdministration.Spot')),
            ],
            bases=('CemeteryAdministration.nryear',),
        ),
        migrations.CreateModel(
            name='OwnershipReceipt',
            fields=[
                ('nryear_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='CemeteryAdministration.NrYear', serialize=False, parent_link=True)),
                ('value', models.FloatField()),
            ],
            bases=('CemeteryAdministration.nryear',),
        ),
        migrations.DeleteModel(
            name='Concesiune',
        ),
        migrations.AddField(
            model_name='yearlypayment',
            name='spot',
            field=models.ForeignKey(to='CemeteryAdministration.Spot'),
        ),
        migrations.AddField(
            model_name='operation',
            name='spot',
            field=models.ForeignKey(to='CemeteryAdministration.Spot'),
        ),
        migrations.AddField(
            model_name='maintenencelevel',
            name='spot',
            field=models.ForeignKey(to='CemeteryAdministration.Spot'),
        ),
        migrations.AddField(
            model_name='construction',
            name='construction_company',
            field=models.ForeignKey(to='CemeteryAdministration.ConstructionCompany', null=True),
        ),
        migrations.AddField(
            model_name='construction',
            name='owner_builder',
            field=models.ForeignKey(to='CemeteryAdministration.Owner', null=True),
        ),
        migrations.AddField(
            model_name='yearlypayment',
            name='receipt',
            field=models.ForeignKey(to='CemeteryAdministration.ContributionReceipt'),
        ),
    ]

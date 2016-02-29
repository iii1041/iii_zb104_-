# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='apriori',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ap_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('Area_id', models.IntegerField(serialize=False, primary_key=True)),
                ('Area_name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Art_To_Att',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('A_id', models.IntegerField(serialize=False, primary_key=True)),
                ('A_date', models.CharField(max_length=100, null=True)),
                ('A_name', models.CharField(max_length=100, null=True)),
                ('A_content', models.CharField(max_length=3000, null=True)),
                ('A_url', models.CharField(max_length=100, null=True)),
                ('A_source', models.CharField(max_length=10, null=True)),
                ('attr_in_art_count', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Attraction',
            fields=[
                ('Attr_id', models.IntegerField(serialize=False, primary_key=True)),
                ('Attr_name', models.CharField(max_length=20)),
                ('Attr_longitude', models.FloatField()),
                ('Attr_latitude', models.FloatField()),
                ('Attr_address', models.CharField(max_length=30)),
                ('Attr_tel', models.CharField(max_length=30, null=True)),
                ('Attr_opentime', models.CharField(max_length=10, null=True)),
                ('Attr_endtime', models.CharField(max_length=10, null=True)),
                ('Attr_hot', models.IntegerField()),
                ('Area', models.ForeignKey(to='iiimap.Area')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('C_id', models.IntegerField(serialize=False, primary_key=True)),
                ('C_date', models.IntegerField()),
                ('C_content', models.CharField(max_length=500)),
                ('Attr', models.ForeignKey(to='iiimap.Attraction')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('T_name', models.CharField(max_length=20)),
                ('T_count', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag_To_Att',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('Attr', models.ForeignKey(to='iiimap.Attraction')),
                ('tag', models.ForeignKey(to='iiimap.Tag')),
            ],
        ),
        migrations.CreateModel(
            name='weather',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('W_year', models.IntegerField()),
                ('W_month', models.IntegerField()),
                ('W_day', models.IntegerField()),
                ('W_hitemp', models.FloatField()),
                ('W_lowtemp', models.FloatField()),
            ],
        ),
        migrations.AddField(
            model_name='art_to_att',
            name='Article',
            field=models.ForeignKey(to='iiimap.Article'),
        ),
        migrations.AddField(
            model_name='art_to_att',
            name='Attr',
            field=models.ForeignKey(to='iiimap.Attraction'),
        ),
        migrations.AddField(
            model_name='apriori',
            name='Attr',
            field=models.ForeignKey(to='iiimap.Attraction'),
        ),
    ]

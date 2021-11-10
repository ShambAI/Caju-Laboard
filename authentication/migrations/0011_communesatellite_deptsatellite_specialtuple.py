# Generated by Django 3.2.5 on 2021-11-08 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0010_alteiadata'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommuneSatellite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=200, unique=True)),
                ('department', models.CharField(max_length=200, unique=True)),
                ('commune', models.CharField(max_length=200, unique=True)),
                ('cashew_tree_cover', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DeptSatellite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=200, unique=True)),
                ('department', models.CharField(max_length=200, unique=True)),
                ('cashew_tree_cover', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SpecialTuple',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('special_id_tuple', models.CharField(max_length=200, unique=True)),
                ('special_id', models.CharField(max_length=200, unique=True)),
            ],
        ),
    ]

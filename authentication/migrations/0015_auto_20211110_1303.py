# Generated by Django 3.2.5 on 2021-11-10 12:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0014_auto_20211109_1514'),
    ]

    operations = [
        migrations.RenameField(
            model_name='specialtuple',
            old_name='special_id',
            new_name='alteia_id',
        ),
        migrations.RenameField(
            model_name='specialtuple',
            old_name='special_id_tuple',
            new_name='plantation_id',
        ),
    ]
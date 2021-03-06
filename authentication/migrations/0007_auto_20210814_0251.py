# Generated by Django 3.2.5 on 2021-08-14 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_auto_20210813_1454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='yieldhistory',
            name='product_id',
            field=models.CharField(max_length=60, unique=True),
        ),
        migrations.AlterField(
            model_name='yieldhistory',
            name='total_dead_trees',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='yieldhistory',
            name='total_plants',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='yieldhistory',
            name='total_sick_trees',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='yieldhistory',
            name='total_trees_out_of_prod',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='yieldhistory',
            name='total_yield_kg',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='yieldhistory',
            name='total_yield_per_ha_kg',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='yieldhistory',
            name='total_yield_per_tree_kg',
            field=models.FloatField(),
        ),
    ]

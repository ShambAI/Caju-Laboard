# Generated by Django 3.2.5 on 2021-07-25 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mothertree',
            name='owner_gender',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('female', 'Others')], default='others', max_length=6),
        ),
        migrations.AlterField(
            model_name='nursery',
            name='owner_gender',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('female', 'Others')], default='others', max_length=6),
        ),
        migrations.AlterField(
            model_name='plantation',
            name='owner_gender',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('female', 'Others')], default='others', max_length=6),
        ),
    ]
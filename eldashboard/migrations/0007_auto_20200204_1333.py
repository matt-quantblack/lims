# Generated by Django 3.0.2 on 2020-02-04 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eldashboard', '0006_auto_20200204_1331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contacts',
            name='lastname',
            field=models.CharField(blank=True, default='', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='contacts',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=25, null=True),
        ),
    ]

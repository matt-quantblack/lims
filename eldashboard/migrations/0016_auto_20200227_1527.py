# Generated by Django 3.0.3 on 2020-02-27 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eldashboard', '0015_auto_20200227_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sampletests',
            name='testunits',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]
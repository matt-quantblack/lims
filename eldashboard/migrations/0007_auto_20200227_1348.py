# Generated by Django 3.0.3 on 2020-02-27 02:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eldashboard', '0006_auto_20200227_1248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testmethods',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]
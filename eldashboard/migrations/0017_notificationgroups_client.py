# Generated by Django 3.0.3 on 2020-02-28 00:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eldashboard', '0016_auto_20200227_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationgroups',
            name='client',
            field=models.ForeignKey(default=2914, on_delete=django.db.models.deletion.CASCADE, to='eldashboard.Clients'),
            preserve_default=False,
        ),
    ]

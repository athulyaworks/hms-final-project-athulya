# Generated by Django 5.1.2 on 2025-07-03 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0006_patient_condition'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='available_time_from',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='doctor',
            name='available_time_to',
            field=models.TimeField(blank=True, null=True),
        ),
    ]

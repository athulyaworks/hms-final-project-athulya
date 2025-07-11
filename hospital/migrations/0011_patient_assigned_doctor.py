# Generated by Django 5.1.2 on 2025-07-04 05:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0010_admissionrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='assigned_doctor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='patients', to='hospital.doctor'),
        ),
    ]

# Generated by Django 5.2.1 on 2025-06-26 08:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hospital', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LabTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_type', models.CharField(choices=[('blood', 'Blood Test'), ('xray', 'X-Ray'), ('mri', 'MRI'), ('urine', 'Urine Test')], max_length=50)),
                ('requested_date', models.DateField(auto_now_add=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('report_file', models.FileField(blank=True, null=True, upload_to='lab_reports/')),
                ('remarks', models.TextField(blank=True)),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='hospital.doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hospital.patient')),
            ],
        ),
    ]

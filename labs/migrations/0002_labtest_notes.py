# Generated by Django 5.1.2 on 2025-07-03 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='labtest',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]

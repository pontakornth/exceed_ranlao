# Generated by Django 4.0.2 on 2022-02-17 10:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ranlao', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisitorLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_time', models.DateTimeField()),
                ('amount', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
            ],
        ),
    ]

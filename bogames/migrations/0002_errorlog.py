# Generated by Django 3.1.3 on 2020-11-29 18:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bogames', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ErrorLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=datetime.datetime.now)),
                ('status_code', models.IntegerField(blank=True, null=True)),
                ('error', models.TextField()),
                ('notes', models.TextField(blank=True, null=True)),
                ('source_url', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
    ]

# Generated by Django 3.1.3 on 2020-12-03 20:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bogames', '0011_auto_20201203_1910'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datagameplayer',
            name='is_current_player',
        ),
    ]

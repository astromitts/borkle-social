# Generated by Django 3.1.3 on 2020-12-03 18:20

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('bogames', '0008_auto_20201203_1432'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datagameplayer',
            name='_data',
        ),
        migrations.AddField(
            model_name='datagameplayer',
            name='data',
            field=jsonfield.fields.JSONField(blank=True, default=dict),
        ),
    ]

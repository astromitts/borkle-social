# Generated by Django 3.1.3 on 2020-12-03 14:27

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('bogames', '0006_datagameplayer_is_current_player'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datagameplayer',
            name='_data',
            field=jsonfield.fields.JSONField(default=dict),
        ),
    ]

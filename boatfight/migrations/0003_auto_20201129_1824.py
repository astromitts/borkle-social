# Generated by Django 3.1.3 on 2020-11-29 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boatfight', '0002_auto_20201128_2238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameplayer',
            name='status',
            field=models.CharField(choices=[('challenged', 'challenged'), ('accepted', 'accepted'), ('ready', 'ready'), ('won', 'won'), ('lost', 'lost')], default='challenged', max_length=10),
        ),
    ]

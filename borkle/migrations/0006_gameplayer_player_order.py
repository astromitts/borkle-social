# Generated by Django 3.1.3 on 2020-11-15 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('borkle', '0005_auto_20201115_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameplayer',
            name='player_order',
            field=models.IntegerField(default=1),
        ),
    ]

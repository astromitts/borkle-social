# Generated by Django 3.1.3 on 2020-12-01 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boatfight', '0004_boatfightgame_game_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameplayer',
            name='status',
            field=models.CharField(choices=[('challenged', 'challenged'), ('accepted', 'accepted'), ('conceded', 'conceded'), ('ready', 'ready'), ('won', 'won'), ('lost', 'lost')], default='challenged', max_length=10),
        ),
    ]
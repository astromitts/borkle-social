# Generated by Django 3.1.3 on 2020-11-28 17:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bogames', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoatFightGame',
            fields=[
                ('game_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bogames.game')),
            ],
            bases=('bogames.game',),
        ),
        migrations.CreateModel(
            name='GamePlayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('challenged', 'challenged'), ('accepted', 'accepted'), ('ready', 'ready')], default='challenged', max_length=10)),
                ('is_current_player', models.BooleanField(default=False)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boatfight.boatfightgame')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bogames.player')),
            ],
        ),
        migrations.CreateModel(
            name='Turn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('turn_index', models.IntegerField(default=1)),
                ('status', models.CharField(choices=[('active', 'active'), ('over', 'over')], default='active', max_length=10)),
                ('shot_1_x', models.IntegerField(default=0)),
                ('shot_1_y', models.IntegerField(default=0)),
                ('shot_1_status', models.CharField(choices=[('hit', 'hit'), ('miss', 'miss'), ('na', 'na')], default='na', max_length=10)),
                ('shot_2_x', models.IntegerField(default=0)),
                ('shot_2_y', models.IntegerField(default=0)),
                ('shot_2_status', models.CharField(choices=[('hit', 'hit'), ('miss', 'miss'), ('na', 'na')], default='na', max_length=10)),
                ('shot_3_x', models.IntegerField(default=0)),
                ('shot_3_y', models.IntegerField(default=0)),
                ('shot_3_status', models.CharField(choices=[('hit', 'hit'), ('miss', 'miss'), ('na', 'na')], default='na', max_length=10)),
                ('shot_4_x', models.IntegerField(default=0)),
                ('shot_4_y', models.IntegerField(default=0)),
                ('shot_4_status', models.CharField(choices=[('hit', 'hit'), ('miss', 'miss'), ('na', 'na')], default='na', max_length=10)),
                ('shot_5_x', models.IntegerField(default=0)),
                ('shot_5_y', models.IntegerField(default=0)),
                ('shot_5_status', models.CharField(choices=[('hit', 'hit'), ('miss', 'miss'), ('na', 'na')], default='na', max_length=10)),
                ('gameplayer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boatfight.gameplayer')),
            ],
        ),
        migrations.CreateModel(
            name='BoatPlacement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('carrier_status', models.CharField(choices=[('active', 'active'), ('sunk', 'sunk')], default='active', max_length=10)),
                ('carrier_1_x', models.IntegerField(default=0)),
                ('carrier_1_y', models.IntegerField(default=0)),
                ('carrier_1_hit', models.BooleanField(default=False)),
                ('carrier_2_x', models.IntegerField(default=0)),
                ('carrier_2_y', models.IntegerField(default=0)),
                ('carrier_2_hit', models.BooleanField(default=False)),
                ('carrier_3_x', models.IntegerField(default=0)),
                ('carrier_3_y', models.IntegerField(default=0)),
                ('carrier_3_hit', models.BooleanField(default=False)),
                ('carrier_4_x', models.IntegerField(default=0)),
                ('carrier_4_y', models.IntegerField(default=0)),
                ('carrier_4_hit', models.BooleanField(default=False)),
                ('carrier_5_x', models.IntegerField(default=0)),
                ('carrier_5_y', models.IntegerField(default=0)),
                ('carrier_5_hit', models.BooleanField(default=False)),
                ('battleship_status', models.CharField(choices=[('active', 'active'), ('sunk', 'sunk')], default='active', max_length=10)),
                ('battleship_1_x', models.IntegerField(default=0)),
                ('battleship_1_y', models.IntegerField(default=0)),
                ('battleship_1_hit', models.BooleanField(default=False)),
                ('battleship_2_x', models.IntegerField(default=0)),
                ('battleship_2_y', models.IntegerField(default=0)),
                ('battleship_2_hit', models.BooleanField(default=False)),
                ('battleship_3_x', models.IntegerField(default=0)),
                ('battleship_3_y', models.IntegerField(default=0)),
                ('battleship_3_hit', models.BooleanField(default=False)),
                ('battleship_4_x', models.IntegerField(default=0)),
                ('battleship_4_y', models.IntegerField(default=0)),
                ('battleship_4_hit', models.BooleanField(default=False)),
                ('cruiser_status', models.CharField(choices=[('active', 'active'), ('sunk', 'sunk')], default='active', max_length=10)),
                ('cruiser_1_x', models.IntegerField(default=0)),
                ('cruiser_1_y', models.IntegerField(default=0)),
                ('cruiser_1_hit', models.BooleanField(default=False)),
                ('cruiser_2_x', models.IntegerField(default=0)),
                ('cruiser_2_y', models.IntegerField(default=0)),
                ('cruiser_2_hit', models.BooleanField(default=False)),
                ('cruiser_3_x', models.IntegerField(default=0)),
                ('cruiser_3_y', models.IntegerField(default=0)),
                ('cruiser_3_hit', models.BooleanField(default=False)),
                ('submarine_status', models.CharField(choices=[('active', 'active'), ('sunk', 'sunk')], default='active', max_length=10)),
                ('submarine_1_x', models.IntegerField(default=0)),
                ('submarine_1_y', models.IntegerField(default=0)),
                ('submarine_1_hit', models.BooleanField(default=False)),
                ('submarine_2_x', models.IntegerField(default=0)),
                ('submarine_2_y', models.IntegerField(default=0)),
                ('submarine_2_hit', models.BooleanField(default=False)),
                ('submarine_3_x', models.IntegerField(default=0)),
                ('submarine_3_y', models.IntegerField(default=0)),
                ('submarine_3_hit', models.BooleanField(default=False)),
                ('destroyer_status', models.CharField(choices=[('active', 'active'), ('sunk', 'sunk')], default='active', max_length=10)),
                ('destroyer_1_x', models.IntegerField(default=0)),
                ('destroyer_1_y', models.IntegerField(default=0)),
                ('destroyer_1_hit', models.BooleanField(default=False)),
                ('destroyer_2_x', models.IntegerField(default=0)),
                ('destroyer_2_y', models.IntegerField(default=0)),
                ('destroyer_2_hit', models.BooleanField(default=False)),
                ('player', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='boatfight.gameplayer')),
            ],
        ),
    ]

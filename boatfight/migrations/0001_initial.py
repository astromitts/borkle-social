# Generated by Django 3.1.3 on 2020-12-05 18:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bogames', '0003_auto_20201204_2316'),
    ]

    operations = [
        migrations.CreateModel(
            name='Boat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.JSONField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='BoatFightGame',
            fields=[
                ('game_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bogames.game')),
                ('game_type', models.CharField(choices=[('salvo', 'Salvo'), ('classic', 'Classic')], max_length=10)),
            ],
            bases=('bogames.game',),
        ),
        migrations.CreateModel(
            name='GamePlayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('challenged', 'challenged'), ('accepted', 'accepted'), ('conceded', 'conceded'), ('ready', 'ready'), ('won', 'won'), ('lost', 'lost')], default='challenged', max_length=10)),
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
                ('status', models.CharField(choices=[('pending', 'pending'), ('active', 'active'), ('over', 'over')], default='pending', max_length=10)),
                ('shots', models.JSONField(blank=True, default=[])),
                ('gameplayer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boatfight.gameplayer')),
            ],
        ),
        migrations.CreateModel(
            name='GamePlayerBoard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ready', models.BooleanField(default=False)),
                ('longship', models.JSONField(blank=True)),
                ('knarr', models.JSONField(blank=True)),
                ('karve', models.JSONField(blank=True)),
                ('kraken', models.JSONField(blank=True)),
                ('faering', models.JSONField(blank=True)),
                ('gameplayer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='boatfight.gameplayer')),
            ],
        ),
    ]

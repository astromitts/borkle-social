from django.db import models
from namer.models import get_random_name
from django.contrib.auth.models import User

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Max

import uuid
import random
from namer.models import get_random_name


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return '<Player {}> {}'.format(self.pk, self.user.username)

    @property
    def username(self):
        return self.user.username

    def join_game(self, game, gameplayer_class):
        gameplayer = gameplayer_class.objects.get(player=self, game=game)
        gameplayer.ready = True
        gameplayer.save()
        return gameplayer

    def decline_game(self, game, gameplayer_class):
        gameplayer = gameplayer_class.objects.get(player=self, game=game)
        gameplayer.delete()

    @classmethod
    def get_by_username(cls, username):
        user = User.objects.filter(username__iexact=username).first()
        if user:
            return cls.objects.get(user=user)
        return None

    @classmethod
    def get_or_create(cls, user):
        player_qs = cls.objects.filter(user=user)
        if player_qs.exists():
            return player_qs.first()
        else:
            new_player = cls(user=user)
            new_player.save()
        return new_player


class Game(models.Model):
    created_by = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    status = models.CharField(
        max_length=20,
        choices=(
            ('waiting', 'waiting'),
            ('active', 'active'),
            ('over', 'over')
        ),
        default='waiting'

    )
    code_name = models.CharField(max_length=100, default=get_random_name, blank=True, unique=True)
    current_turn_index = models.IntegerField(default=1)


    def __str__(self):
        if self.code_name:
            return 'Game {}'.format(self.code_name)
        else:
            return 'Unsaved Game'

    def set_status(self):
        if self.all_players_ready and self.status == 'waiting':
            self.start_game()

    @property
    def all_players_ready(self):
        ready_player_count = self.gameplayer_set.filter(status='ready').count()
        return ready_player_count == self.gameplayer_set.all().count()

    @classmethod
    def initialize_game(cls, players, gameplayer_class):
        newgame = cls(
            status='pending'
        )
        newgame.save()
        for player in players:
            gp = gameplayer_class(
                player=player,
                game=newgame
            )
            gp.save()
        return newgame

    def start_game(self):
        self.status = 'active'
        self.save()
        first_player = random.choice(self.gameplayer_set.all())
        first_player.start_turn()

    def boot_player(self, gameplayer):
        if gameplayer.is_current_player:
            self.advance_player()
        gameplayer.delete()

    @property
    def current_player(self):
        if self.gameplayer_set.count() == 1:
            return self.gameplayer_set.first()
        return self.gameplayer_set.filter(is_current_player=True).first()

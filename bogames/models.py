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

    def join_game(self, game):
        gameplayer = GamePlayer.objects.get(player=self, game=game)
        gameplayer.ready = True
        gameplayer.save()
        if game.all_players_ready:
            game.start_game()

    def decline_game(self, game):
        gameplayer = GamePlayer.objects.get(player=self, game=game)
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

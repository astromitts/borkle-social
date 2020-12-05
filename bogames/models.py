from django.db import models
from namer.models import get_random_name
from django.contrib.auth.models import User

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Max
from django.utils.timezone import now

from datetime import datetime

import json
import uuid
import random
from namer.models import get_random_name


class ErrorLog(models.Model):
    """ Cheat around need for setting up real logs
    """
    timestamp = models.DateTimeField(default=now)
    status_code = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=300, blank=True, null=True)
    error = models.TextField()
    notes = models.TextField(blank=True, null=True)
    source_url = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return 'Error: {}, {}'.format(self.timestamp, self.title)


class Player(models.Model):
    """ Represents a unique site user and links to their Django User instance
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return '<Player {}> {}'.format(self.pk, self.user.username)

    @property
    def username(self):
        return self.user.username

    def join_game(self, game, gameplayer_class):
        gameplayer = gameplayer_class.objects.get(player=self, game=game)
        if hasattr(gameplayer, 'ready'):
            gameplayer.ready = True
        elif hasattr(gameplayer, 'data'):
            gameplayer.data['status'] = 'ready'
        elif hasattr(gameplayer, 'status'):
            gameplayer.status = 'ready'

        gameplayer.save()
        if game.all_players_ready:
            game.start_game()
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
    """ Base class for a game model with fields common to all games
        Includes common methods and properties that should work on any
        game unless overwritten

        There is an expectation that child Game models will have a GamePlayer
        model defined and linked to it via FKeys
    """
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
        """ If all players have accepted the game invitation and
            the Game status is still 'waiting', kick off the start_game function
        """
        if self.all_players_ready and self.status == 'waiting':
            self.start_game()

    @property
    def all_players_ready(self):
        """ Returns Boolean True if all players in the game are ready
        """
        ready_player_count = self.gameplayer_set.filter(status='ready').count()
        return ready_player_count == self.gameplayer_set.all().count()

    @classmethod
    def initialize_game(cls, players, gameplayer_class):
        """ Initialize a new Game instance
        """
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
        """ Set Game status to active and start the first turn for a random player
        """
        self.status = 'active'
        self.save()
        first_player = random.choice(self.gameplayer_set.all())
        first_player.start_turn()

    def boot_player(self, gameplayer):
        """ Remove a player from a Game
        """
        if gameplayer.is_current_player:
            self.advance_player()
        gameplayer.delete()

    @property
    def current_player(self):
        """ Return the GamePlayer instance for the player with is_current_player status
        """
        if self.gameplayer_set.count() == 1:
            return self.gameplayer_set.first()
        return self.gameplayer_set.filter(is_current_player=True).first()

    def get_gameplayer(self, player):
        """ Get the GamePlayer instance of given Player
        """
        return self.gameplayer_set.filter(player=player).first()



class GamePlayer(models.Model):
    """ GamePlayer Model for BoatFight Game
    """
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='base_gameplayer')
    status = models.CharField(
        max_length=10,
        choices=(
            ('challenged', 'challenged'),
            ('accepted', 'accepted'),
            ('conceded', 'conceded'),
            ('ready', 'ready'),
            ('won', 'won'),
            ('lost', 'lost'),
        ),
        default='challenged'
    )
    is_current_player = models.BooleanField(default=False)

    def __str__(self):
        return '<GamePlayer: {}, {}>'.format(self.pk, self.player.username)


class DataGame(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    code_name = models.CharField(max_length=100, default=get_random_name, blank=True, unique=True)
    meta = models.JSONField(blank=True)
    data = models.JSONField(blank=True)

    def __str__(self):
        return json.dumps(self.meta)

    @property
    def _default_game_meta(self):
        return {
            'gameStatus': 'pending',
            'codeName': self.code_name,
            'uuid': str(self.uuid),
        }

    @property
    def _default_game_data(self):
        return {}

    @property
    def status(self):
        return self.meta['gameStatus']

    @property
    def all_players(self):
        players = []
        for player in self.gameplayer_set.all():
            players.append(player.data)

    def get_opponent_for_local_player(self, local_player):
        return self.gameplayer_set.exclude(pk=local_player.pk).first()

    def get_player_set(self, local_player):
        opponent = self.get_opponent_for_local_player(local_player)
        if not opponent:
            opponent_data = {}
        else:
            opponent_data = opponent.data

        return {
            'player': local_player.data,
            'opponent': opponent_data
        }

    def update_meta(self, key, value):
        self.meta[key] = value
        self.save()

    def update_data(self, key, value):
        self.data[key] = value
        self.save()

    def save(self):
        if not self.data:
            self.data = self._default_game_data
        if not self.meta:
            self.meta = self._default_game_meta
        super(DataGame, self).save()

    @property
    def all_players_ready(self):
        for gp in self.gameplayer_set.all():
            if gp.data['status'] not in ['active', 'ready', 'won', 'lost']:
                return False
        return True

    def get_gameplayer(self, player):
        """ Get the GamePlayer instance of given Player
        """
        return self.gameplayer_set.filter(player=player).first()

    @property
    def current_player(self):
        self.gameplayer_set.filter(data__isCurrentPlayer=True).first()

    def start_game(self):
        """ Set Game status to active and start the first turn for a random player
        """
        self.meta.update({'gameStatus': 'active'})
        first_player = random.choice(self.gameplayer_set.all())
        if first_player:
            first_player.start_turn()
        self.save()

    @classmethod
    def initialize_game(cls, players, gameplayer_class):
        """ Initialize a new Game instance
        """
        newgame = cls()
        newgame.save()
        for player in players:
            gp = gameplayer_class(
                player=player,
                game=newgame
            )
            gp.save()
        return newgame


class DataGamePlayer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='database_gameplayer')
    data = models.JSONField(blank=True)

    def _default_data(self):
        return {
            "id": self.pk,
            "playerId": self.player.pk,
            "userName": self.username,
            "status": "waiting",
            "isCurrentPlayer": False,
            "gameUUID": str(self.game.uuid),
        }

    @property
    def str_keys(self):
        return ['id', 'playerId', 'userName', 'status', 'isCurrentPlayer', 'gameUUID']


    def __str__(self):
        str_data = {}
        for key in self.str_keys:
            str_data[key] = self.data.get(key)
        return json.dumps(str_data)

    @property
    def username(self):
        return self.player.username

    @property
    def status(self):
        return self.data['status']

    @property
    def opponent(self):
        return self.game.get_opponent_for_local_player(self)


    def set_status(self, status):
        self.data['status'] = status
        self.save()

    def start_turn(self):
        opponent = self.opponent
        opponent.data['isCurrentPlayer'] = False
        opponent.save()

        self.data['isCurrentPlayer'] = True
        self.save()


    def save(self):
        if not self.data:
            self.data = self._default_data
        super(DataGamePlayer, self).save()
        if not self.data["id"]:
            self.data["id"] = self.pk
            self.save()

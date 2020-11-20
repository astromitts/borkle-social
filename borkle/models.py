from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Max
import uuid
import random

from borkle.score import Score
from namer.models import get_random_name


class Player(models.Model):
    user = models.ForeignKey(User, unique=True, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return '<Player {}> {}'.format(self.pk, self.user.username)

    def join_game(self, game):
        gameplayer = GamePlayer.objects.get(player=self, game=game)
        gameplayer.ready = True
        gameplayer.save()

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

    @ property
    def all_games(self):
        games = {'active': [], 'pending': [], 'invitations': [], 'completed': []}
        for gp in self.gameplayer_set.all():
            game_status = gp.game.get_status()
            if game_status == 'active':
                games['active'].append(gp.game)
            elif game_status == 'waiting' and gp.ready:
                games['pending'].append(gp.game)
            elif game_status == 'waiting' and not gp.ready:
                games['invitations'].append(gp.game)
            elif game_status == 'over':
                games['completed'].append(gp.game)

        return games


class Game(models.Model):
    created_by = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL)
    max_score = models.IntegerField(default=10000)
    num_players = models.IntegerField(default=1)
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
    action_count = models.IntegerField(default=1)
    last_turn = models.BooleanField(default=False)

    def __str__(self):
        return 'Game {}'.format(self.code_name)

    @classmethod
    def create(cls, max_score, invited_players, initial_player, code_name_prefix=None):
        game = cls(max_score=max_score, num_players=len(invited_players) + 1, created_by=initial_player)
        game.save()
        if code_name_prefix:
            game.code_name = '{}-{}'.format(code_name_prefix, game.code_name)
            game.save()
        initial_gameplayer = GamePlayer(player=initial_player, game=game, ready=True)
        initial_gameplayer.save()
        for player in invited_players:
            gameplayer = GamePlayer(player=player, game=game, ready=False)
            gameplayer.save()

        order = 1
        for player in game.gameplayer_set.order_by('?').all():
            player.player_order = order
            player.save()
            order += 1

        return game, initial_gameplayer

    def end_game(self):
        self.status = 'over'
        self.save()

    @property
    def winner(self):
        winner = None
        max_score = self.gameplayer_set.all().aggregate(maxscore=Max('total_score'))['maxscore']
        winner_qs = self.gameplayer_set.filter(total_score=max_score)
        return winner_qs.all()

    def update_action_count(self):
        self.action_count += 1
        self.save()

    def get_player_links(self, exclude_initial_player):
        links = []
        for gameplayer in self.gameplayer_set.exclude(pk=exclude_initial_player.pk).all():
            links.append(gameplayer.game_invitation_link)
        return links

    @property
    def all_players_ready(self):
        ready_player_count = self.gameplayer_set.filter(ready=True).count()
        return ready_player_count == self.gameplayer_set.all().count()

    @property
    def current_player(self):
        if self.gameplayer_set.count() == 1:
            return self.gameplayer_set.first()
        return self.gameplayer_set.filter(is_current_player=True).first()

    @property
    def set_count(self):
        set_count = 0
        for turn in self.turn_set.all():
            set_count += turn.scoreset_set.count()
        return set_count

    def get_status(self):
        if self.all_players_ready and self.status == 'waiting':
            self.start_game()
        elif self.all_players_had_last_turn and self.status == 'active':
            self.status = 'over'
            self.end_game()
        return self.status

    @property
    def all_players_had_last_turn(self):
        return self.gameplayer_set.filter(had_last_turn=True).count() == self.gameplayer_set.all().count()

    def start_game(self):
        self.status = 'active'
        self.save()
        first_player = random.choice(self.gameplayer_set.all())
        first_player.start_turn()

    def advance_player(self):
        if self.gameplayer_set.count() == 1:
            self.current_player.end_turn()
            self.current_turn_index += 1
            self.save()
            if self.current_player.total_score >= self.max_score:
                self.end_game()
            else:
                self.current_player.start_turn()
        else:
            current_player_order = self.current_player.player_order
            if current_player_order == self.gameplayer_set.count():
                next_player = self.gameplayer_set.get(player_order=1)
                self.current_turn_index += 1
                self.save()
            else:
                next_player = self.gameplayer_set.get(player_order=current_player_order + 1)
            self.current_player.end_turn()

            if self.all_players_had_last_turn:
                self.end_game()
            else:
                next_player.start_turn()

    @property
    def turn_history(self):
        history = {}
        for i in reversed(range(1, self.current_turn_index + 1)):
            for player in self.gameplayer_set.all():
                player_history = history.get(player, {})
                player_turn = player.turn_set.filter(turn_index=i).first()
                if player_turn:
                    player_history[i] = {
                        'total_score': player_turn.score,
                        'scoresets': player_turn.scoreset_set.order_by('-pk')
                    }
                else:
                    player_history[i] = []
                history[player] = player_history
        return history


    def save(self, *args, **kwargs):
        if not self.code_name:
            has_name = False
            while not has_name:
                random_name = get_random_name()
                is_dupe = Game.objects.filter(code_name=random_name).count() >= 1
                if not is_dupe:
                    has_name = True

            self.code_name = random_name
        super(Game, self).save(*args, **kwargs)


    def boot_player(self, gameplayer):
        if gameplayer.is_current_player:
            self.advance_player()
        gameplayer.delete()


class GamePlayer(models.Model):
    player = models.ForeignKey(Player, null=True, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    ready = models.BooleanField(default=False)
    player_order = models.IntegerField(default=1)
    is_current_player = models.BooleanField(default=False)
    total_score = models.IntegerField(default=0)
    had_last_turn = models.BooleanField(default=False)

    def __str__(self):
        return '{} > Player: {}'.format(self.game, self.player.user.username)

    @property
    def username(self):
        return self.player.user.username

    @property
    def game_invitation_link(self):
        return reverse('game_accept_invitation_link', kwargs={'game_uuid': self.game.uuid, 'gameplayer_id': self.pk})

    @property
    def current_turn(self):
        return self.turn_set.filter(active=True).first()

    def set_player(self, player):
        self.player = player
        self.ready = True
        self.save()

    def roll_dice(self):
        self.current_turn.roll_dice()
        self.game.update_action_count()
        return self.current_turn.dice_values

    @property
    def rolled_dice(self):
        if self.current_turn:
            return self.current_turn.dice_values
        return []

    @property
    def is_last_turn(self):
        return self.game.last_turn and not self.had_last_turn

    def update_score(self):
        total_score = 0
        for turn in self.turn_set.all():
            total_score += turn.score
        self.total_score = total_score
        self.save()

    def start_turn(self):
        self.is_current_player = True
        self.save()
        new_turn = Turn(
            gameplayer=self,
            game=self.game,
            turn_index=self.game.current_turn_index,
            active=True
        )
        new_turn.save()
        self.game.update_action_count()

    def end_turn(self):
        self.is_current_player = False
        self.current_turn.set_score()
        self.update_score()
        self.current_turn.end_turn()
        self.game.update_action_count()
        if self.total_score >= self.game.max_score:
            self.game.last_turn = True
            self.game.save()
        if self.game.last_turn:
            self.had_last_turn = True
            self.save()


class Turn(models.Model):
    gameplayer = models.ForeignKey(GamePlayer, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    available_dice_count = models.IntegerField(default=6)
    active = models.BooleanField(default=False)
    turn_index = models.IntegerField(default=1)
    has_rolled = models.BooleanField(default=False)
    rolled_dice_1_value = models.IntegerField(blank=True, null=True)
    rolled_dice_2_value = models.IntegerField(blank=True, null=True)
    rolled_dice_3_value = models.IntegerField(blank=True, null=True)
    rolled_dice_4_value = models.IntegerField(blank=True, null=True)
    rolled_dice_5_value = models.IntegerField(blank=True, null=True)
    rolled_dice_6_value = models.IntegerField(blank=True, null=True)
    borkle = models.BooleanField(default=False)

    def __str__(self):
        if self.active:
            active_str = ' (active)'
        else:
            active_str = ''
        return '{} turn: {}{}'.format(self.gameplayer, self.pk, active_str)

    @property
    def dice_fields(self):
        return [
            {'field': 'rolled_dice_1_value', 'min_needed': 1},
            {'field': 'rolled_dice_2_value', 'min_needed': 2},
            {'field': 'rolled_dice_3_value', 'min_needed': 3},
            {'field': 'rolled_dice_4_value', 'min_needed': 4},
            {'field': 'rolled_dice_5_value', 'min_needed': 5},
            {'field': 'rolled_dice_6_value', 'min_needed': 6},
        ]

    def set_score(self):
        self.score = self.current_score
        self.save()


    def end_turn(self):
        self.active = False
        self.scoreset_set.all().update(locked=True)
        self.save()

    def roll_dice(self):
        self.scoreset_set.all().update(locked=True)
        if self.available_dice_count == 0:
            self.available_dice_count = 6
        for dice_field in self.dice_fields:
            if self.available_dice_count >= dice_field['min_needed']:
                setattr(self, dice_field['field'], random.choice([1, 2, 3, 4, 5, 6]))
            else:
                setattr(self, dice_field['field'], None)
        self.has_rolled = True
        if not self.has_score:
            self.borkle = True
            self.scoreset_set.all().delete()
            borkle_score = ScoreSet(
                turn=self,
                score=0,
                score_type='borkle!'
            )
            borkle_score.save()
        self.save()

    @property
    def dice_values(self):
        dice_values = {}
        dice_fields = [
            'rolled_dice_1_value',
            'rolled_dice_2_value',
            'rolled_dice_3_value',
            'rolled_dice_4_value',
            'rolled_dice_5_value',
            'rolled_dice_6_value'
        ]
        for field in dice_fields:
            value = getattr(self, field)
            if value:
                dice_values[field] = value
        return dice_values

    @property
    def has_score(self):
        value_set = [value for field, value in self.dice_values.items()]
        test_score = Score(value_set)
        return test_score.has_score

    def check_score(self, fields):
        dice_values = [getattr(self, field) for field in fields]
        test_score = Score(dice_values)
        return test_score.score > 0

    def make_selection(self, fields):
        score_set = ScoreSet(
            turn=self
        )
        dice_index = 1
        for field in fields:
            score_set_field = 'scored_dice_{}_value'.format(dice_index)
            dice_value = getattr(self, field)
            setattr(score_set, score_set_field, int(dice_value))
            setattr(self, field, None)
            self.available_dice_count -= 1
            dice_index += 1

        if self.available_dice_count == 0:
            self.available_dice_count = 6

        self.save()
        score_set.save()
        self.game.update_action_count()

    @property
    def current_score(self):
        current_score = 0
        for scoreset in self.scoreset_set.all():
            current_score += scoreset.score
        return current_score

    def undo_score_selection(self, scoreset_id):
        scoreset = self.scoreset_set.filter(pk=scoreset_id).first()
        if scoreset:
            for score in scoreset.scorable_values:
                if not self.rolled_dice_1_value:
                    self.rolled_dice_1_value = score
                elif not self.rolled_dice_2_value:
                    self.rolled_dice_2_value = score
                elif not self.rolled_dice_3_value:
                    self.rolled_dice_4_value = score
                elif not self.rolled_dice_4_value:
                    self.rolled_dice_4_value = score
                elif not self.rolled_dice_5_value:
                    self.rolled_dice_5_value = score
                elif not self.rolled_dice_6_value:
                    self.rolled_dice_6_value = score
                self.available_dice_count += 1
                self.save()
            scoreset.delete()
        self.game.update_action_count()


class ScoreSet(models.Model):
    turn = models.ForeignKey(Turn, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    score_type = models.CharField(max_length=150)
    scored_dice_1_value = models.IntegerField(blank=True, null=True)
    scored_dice_2_value = models.IntegerField(blank=True, null=True)
    scored_dice_3_value = models.IntegerField(blank=True, null=True)
    scored_dice_4_value = models.IntegerField(blank=True, null=True)
    scored_dice_5_value = models.IntegerField(blank=True, null=True)
    scored_dice_6_value = models.IntegerField(blank=True, null=True)
    locked = models.BooleanField(default=False)

    def __str__(self):
        return '{} Score set: {}'.format(self.turn, self.pk)

    @property
    def score_fields(self):
        return [
            self.scored_dice_1_value,
            self.scored_dice_2_value,
            self.scored_dice_3_value,
            self.scored_dice_4_value,
            self.scored_dice_5_value,
            self.scored_dice_6_value,
        ]

    @property
    def scorable_values(self):
        scorable_values = []

        for field in self.score_fields:
            if field:
                scorable_values.append(field)
        return scorable_values

    def save(self, *args, **kwargs):
        score = Score(self.scorable_values)
        self.score = score.score
        self.score_type = score.score_type
        super(ScoreSet, self).save(*args, **kwargs)


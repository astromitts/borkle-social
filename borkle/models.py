from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Max
import uuid
import random

from bogames.models import Game, Player
from borkle.score import Score

from django.db import models
from namer.models import get_random_name


class BorkleGame(Game):
    max_score = models.IntegerField(default=10000)
    num_players = models.IntegerField(default=1)
    last_turn = models.BooleanField(default=False)
    game_type = models.CharField(
        max_length=25,
        choices=(('practice', 'practice'), ('normal', 'normal')),
        default='normal'
    )

    @classmethod
    def create(cls, max_score, invited_players, initial_player, code_name_prefix=None, game_type='normal'):
        game = cls()
        game.max_score = max_score
        game.num_players = len(invited_players) + 1
        game.created_by = initial_player
        game.game_type = game_type
        game.save()
        if code_name_prefix:
            game.code_name = '{}-{}'.format(code_name_prefix, game.code_name)
            game.save()
        initial_borkleplayer = BorklePlayer(player=initial_player, game=game, ready=True)
        initial_borkleplayer.save()
        for player in invited_players:
            borkleplayer = BorklePlayer(player=player, game=game, ready=False)
            borkleplayer.save()

        order = 1
        for player in game.borkleplayer_set.order_by('?').all():
            player.player_order = order
            player.save()
            order += 1

        return game, initial_borkleplayer

    def start_turn(self):
        self.is_current_player = True
        self.save()
        new_turn = Turn(
            borkleplayer=self,
            game=self.game,
            turn_index=self.game.current_turn_index,
            active=True
        )
        new_turn.save()

    def end_turn(self):
        self.is_current_player = False
        self.current_turn.set_score()
        self.update_score()
        self.current_turn.end_turn()
        if self.total_score >= self.game.max_score:
            self.game.last_turn = True
            self.game.save()
        if self.game.last_turn:
            self.had_last_turn = True
            self.save()

    def update_score(self):
        total_score = 0
        for turn in self.turn_set.all():
            total_score += turn.score
        self.total_score = total_score
        self.save()

    def end_game(self):
        self.status = 'over'
        self.save()

    @property
    def all_players_ready(self):
        ready_player_count = self.borkleplayer_set.filter(ready=True).count()
        return ready_player_count == self.borkleplayer_set.all().count()

    @property
    def current_player(self):
        if self.borkleplayer_set.count() == 1:
            return self.borkleplayer_set.first()
        return self.borkleplayer_set.filter(is_current_player=True).first()

    @property
    def all_players_had_last_turn(self):
        return self.borkleplayer_set.filter(had_last_turn=True).count() == self.borkleplayer_set.all().count()

    def start_game(self):
        self.status = 'active'
        self.save()
        first_player = random.choice(self.borkleplayer_set.all())
        first_player.start_turn()

    def advance_player(self):
        if self.borkleplayer_set.count() == 1:
            self.current_player.end_turn()
            self.current_turn_index += 1
            self.save()
            if self.current_player.total_score >= self.max_score:
                self.end_game()
            else:
                self.current_player.start_turn()
        else:
            current_player_order = self.current_player.player_order
            if current_player_order == self.borkleplayer_set.count():
                next_player = self.borkleplayer_set.get(player_order=1)
                self.current_turn_index += 1
                self.save()
            else:
                next_player = self.borkleplayer_set.get(player_order=current_player_order + 1)
            self.current_player.end_turn()

            if self.all_players_had_last_turn:
                self.end_game()
            else:
                next_player.start_turn()

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


    def get_borkleplayer(self, player):
        return self.borkleplayer_set.filter(player=player).first()

    def boot_player(self, borkleplayer):
        if borkleplayer.is_current_player:
            self.advance_player()
        borkleplayer.delete()

    @property
    def winner(self):
        winner = None
        max_score = self.borkleplayer_set.all().aggregate(maxscore=Max('total_score'))['maxscore']
        winner_qs = self.borkleplayer_set.filter(total_score=max_score)
        return winner_qs.all()

    @property
    def turn_history(self):
        history = {}
        for i in reversed(range(1, self.current_turn_index + 1)):
            for player in self.borkleplayer_set.all():
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

    def get_gameplayer(self, player):
        return self.borkleplayer_set.filter(player=player).first()


class BorklePlayer(models.Model):
    player = models.ForeignKey(Player, null=True, on_delete=models.CASCADE)
    game = models.ForeignKey(BorkleGame, on_delete=models.CASCADE)
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
    def current_turn(self):
        return self.turn_set.filter(active=True).first()

    def set_player(self, player):
        self.player = player
        self.ready = True
        self.save()

    @property
    def rolled_dice(self):
        if self.current_turn:
            return self.current_turn.dice_values
        return []

    @property
    def is_last_turn(self):
        return self.game.last_turn and not self.had_last_turn

    def start_turn(self):
        self.is_current_player = True
        self.save()
        new_turn = Turn(
            borkleplayer=self,
            game=self.game,
            turn_index=self.game.current_turn_index,
            active=True
        )
        new_turn.save()

    def end_turn(self):
        self.is_current_player = False
        self.current_turn.set_score()
        self.update_score()
        self.current_turn.end_turn()
        if self.total_score >= self.game.max_score:
            self.game.last_turn = True
            self.game.save()
        if self.game.last_turn:
            self.had_last_turn = True
            self.save()

    def update_score(self):
        total_score = 0
        for turn in self.turn_set.all():
            total_score += turn.score
        self.total_score = total_score

    @ property
    def all_games(self):
        games = {'active': [], 'pending': [], 'invitations': [], 'completed': []}
        for gp in self.game_set.all():
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


class Turn(models.Model):
    borkleplayer = models.ForeignKey(BorklePlayer, on_delete=models.CASCADE)
    game = models.ForeignKey(BorkleGame, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    active = models.BooleanField(default=False)
    turn_index = models.IntegerField(default=1)
    available_dice_count = models.IntegerField(default=6)
    rolled_dice_1_value = models.IntegerField(blank=True, null=True)
    rolled_dice_2_value = models.IntegerField(blank=True, null=True)
    rolled_dice_3_value = models.IntegerField(blank=True, null=True)
    rolled_dice_4_value = models.IntegerField(blank=True, null=True)
    rolled_dice_5_value = models.IntegerField(blank=True, null=True)
    rolled_dice_6_value = models.IntegerField(blank=True, null=True)

    def __str__(self):
        if self.active:
            active_str = ' (active)'
        else:
            active_str = ''
        return '{} turn: {}{}'.format(self.borkleplayer, self.pk, active_str)

    def end_turn(self):
        self.active = False
        self.scoreset_set.all().update(locked=True)
        self.save()

    @property
    def dice_field_strings(self):
        return [
            'rolled_dice_1_value',
            'rolled_dice_2_value',
            'rolled_dice_3_value',
            'rolled_dice_4_value',
            'rolled_dice_5_value',
            'rolled_dice_6_value'
        ]

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

    def set_roll_dice(self, rolled_dice):
        self.scoreset_set.all().update(locked=True)
        for dice_field, value in rolled_dice.items():
            setattr(self, dice_field, value)
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
        if not self.has_score:
            self.scoreset_set.all().delete()
            borkle_score = ScoreSet(
                turn=self,
                score=0,
                score_type='borkle!'
            )
            borkle_score.save()
        self.save()

    def borkle_turn(self):
        self.scoreset_set.all().delete()
        borkle_score = ScoreSet(
            turn=self,
            score=0,
            score_type='borkle!'
        )
        borkle_score.save()

    @property
    def dice_values(self):
        dice_values = {}
        for field in self.dice_field_strings:
            value = getattr(self, field)
            if value:
                dice_values[field] = value
        return dice_values

    @property
    def scorable_values(self):
        dice_values = []
        for field in self.dice_field_strings:
            rolled_value = getattr(self, field)
            if rolled_value:
                dice_values.append(rolled_value)
            else:
                dice_values.append(None)
        return dice_values


    @property
    def scorable_fields(self):
        scorable_fields = []
        for field in self.dice_field_strings:
            if getattr(self, field):
                scorable_fields.append(field)
            else:
                scorable_fields.append(None)
        return scorable_fields

    def make_selection(self, fields):
        score_set = ScoreSet(
            turn=self,
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


class ScoreSet(models.Model):
    turn = models.ForeignKey(Turn, on_delete=models.CASCADE)
    roll = models.IntegerField(default=1)
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
    def score_field_strings(self):
        return [
            'scored_dice_1_value',
            'scored_dice_2_value',
            'scored_dice_3_value',
            'scored_dice_4_value',
            'scored_dice_5_value',
            'scored_dice_6_value',
        ]

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

    @property
    def scorable_fields(self):
        scorable_fields = []

        for field in self.score_field_strings:
            if getattr(self, field):
                scorable_fields.append(field)
            else:
                scorable_fields.append(None)
        return scorable_fields

    def save(self, *args, **kwargs):
        score = Score(self.scorable_values)
        self.score = score.score
        self.score_type = score.score_type
        super(ScoreSet, self).save(*args, **kwargs)


from django.db import models
from bogames.models import Game, Player
import json


class Boat(models.Model):
    data = models.JSONField(blank=True)

    def __str__(self):
        return self.data.get('label')

class _Boat(object):
    """ Useful Class for storing display information for boats
    """
    def __init__(self, label, units):
        self.label = label
        self.units = units
        self.image = 'images/boats/{}/{}.png'.format(label.lower(), label.lower())
        self.image_map = []
        for i in range(1, self.units + 1):
            self.image_map.append('images/boats/{}/{}.png'.format(label.lower(), i))


SHIPS = {
    'longship': _Boat('Longship', 5),
    'knarr': _Boat('Knarr', 4),
    'karve': _Boat('Karve', 3),
    'kraken': _Boat('Kraken', 3),
    'faering': _Boat('Faering', 2),
}


class BoatFightGame(Game):
    """ BoatFight Game model, inherits bogames.models.Game
    """
    game_type = models.CharField(
        max_length=10,
        choices=(
            ('salvo', 'Salvo'),
            ('classic', 'Classic'),
        )
    )

    def __str__(self):
        return '<BoatFightGame: {}, CodeName: {}, UUID: {}>'.format(self.pk, self.code_name, self.uuid)

    def end_game(self):
        """ Custom logic for how to end a BoatFight game
        """
        self.status = 'over'
        for gp in self.gameplayer_set.all():
            gp.turn_set.all().update(status='over')
            gp.is_current_player = False
            if gp.available_shots > 0:
                gp.status = 'won'
            else:
                gp.status = 'lost'
            gp.save()
        self.save()

    @property
    def winner(self):
        """ Return the GamePlayer with status='won'
        """
        return self.gameplayer_set.filter(status='won').first()

    @property
    def loser(self):
        """ Return the GamePlayer with status='won'
        """
        return self.gameplayer_set.filter(status__in=['lost', 'conceded']).first()

    def set_status(self):
        """ Set game status based on logical context and return it
        """
        if self.status == 'active':
            loser = None
            winner = None
            for gameplayer in self.gameplayer_set.all():
                if gameplayer.gameplayerboard.count_sunk == 5 or gameplayer.status == 'conceded':
                    loser = gameplayer
                else:
                    tmp_winner = gameplayer

            if loser:
                winner = tmp_winner
                self.status = 'over'
                loser.turn_set.all().update(status='over')
                loser.is_current_player = False
                if loser.status != 'conceded':
                    loser.status = 'lost'

                winner.turn_set.all().update(status='over')
                winner.is_current_player = False
                winner.status = 'won'
                loser.save()
                winner.save()
                self.save()
        elif self.all_players_ready and self.status == 'waiting':
            self.start_game()

    def boot_player(self, gameplayer):
        gameplayer.status = 'conceded'
        gameplayer.gameplayerboard.sink_all_ships()
        gameplayer.save()


class GamePlayer(models.Model):
    """ GamePlayer Model for BoatFight Game
    """
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(BoatFightGame, on_delete=models.CASCADE)
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
        return '<GamePlayer: {}, {}> {}'.format(self.pk, self.player.username, self.game)

    @property
    def ships(self):
        return SHIPS

    @property
    def username(self):
        return self.player.username


    @property
    def available_shots(self):
        return len(self.gameplayerboard.boats) - self.gameplayerboard.count_sunk

    @property
    def current_turn(self):
        return self.turn_set.filter(status='active').first()

    def end_turn(self, shots, hits):
        if self.current_turn:
            turn_index = self.current_turn.turn_index
            self.current_turn.end_turn(shots, hits)
        else:
            turn_index = 0
        return turn_index

    def start_turn(self, turn_index=1):
        GamePlayer.objects.filter(is_current_player=True).update(is_current_player=False)
        self.is_current_player = True
        self.save()
        if self.turn_set.filter(turn_index=turn_index).exists():
            turn_index += 1
        new_turn = Turn(
            gameplayer=self,
            turn_index=turn_index,
            status='active'
        )
        new_turn.save()
        return new_turn

    @property
    def all_shots(self):
        all_shots = []
        for turn in self.turn_set.all():
            all_shots = all_shots + turn.shots
        return all_shots


class GamePlayerBoard(models.Model):
    gameplayer = models.OneToOneField(GamePlayer, on_delete=models.CASCADE)
    ready = models.BooleanField(default=False)
    longship = models.JSONField(blank=True)
    knarr = models.JSONField(blank=True)
    karve = models.JSONField(blank=True)
    kraken = models.JSONField(blank=True)
    faering = models.JSONField(blank=True)

    def __str__(self):
        return '<GamePlayerBoard {}> Player: {}, game: "{}" {}>'.format(
            self.pk,
            self.gameplayer.username,
            self.gameplayer.game.code_name,
            str(self.gameplayer.game.uuid)
        )

    @property
    def boats(self):
        return [
            self.longship,
            self.knarr,
            self.karve,
            self.kraken,
            self.faering
        ]

    @property
    def count_sunk(self):
        _count_sunk = 0
        for boat in self.boats:
            if boat['status'] == 'sunk':
                _count_sunk += 1
        return _count_sunk

    def check_shots(self, posted_shots):
        hits = []
        for boat in self.boats:
            hit_count = 0
            for coordinate in boat['coordinates']:
                coordinates_as_list = [
                    coordinate['x'],
                    coordinate['y']
                ]
                if coordinates_as_list in posted_shots:
                    coordinate['hit'] = True
                    hits.append(coordinates_as_list)
                if coordinate['hit']:
                    hit_count += 1
            if hit_count == boat['display']['units']:
                boat['status'] = 'sunk'
        self.save()
        return hits

    @property
    def sunk_boats(self):
        _sunk_boats = []
        for boat in self.boats:
            if boat['status'] == 'sunk':
                _sunk_boats.append(boat)
        return _sunk_boats


    def sink_all_ships(self):
        for boat in self.boats:
            for coordinate in boat['coordinates']:
                coordinate['hit'] = True
            boat['status'] = 'sunk'
        self.save()


    def set_placements(self, boat_placement_post):
        boats = Boat.objects.all()
        for boat in self.boats:
            label = boat['display']['label']
            boat_data = getattr(self, label)
            boat_data['coordinates'] = []
            boat_data['orientation'] = None
            for i in range(1, boat['display']['units'] + 1):
                x_field = '{}_{}_x'.format(label, i)
                y_field = '{}_{}_y'.format(label, i)
                x_coordinate = boat_placement_post.get(x_field)
                y_coordinate = boat_placement_post.get(y_field)
                current_coordinates = {
                    'x': x_coordinate,
                    'y': y_coordinate,
                    'hit': False
                }
                boat_data['coordinates'].append(current_coordinates)
                coordinates_length = len(boat_data['coordinates'])
                if coordinates_length > 1 and not boat_data['orientation']:
                    previous_coordinates = boat_data['coordinates'][0]
                    if previous_coordinates['x'] == current_coordinates['x']:
                        boat_data['orientation'] = 'vertical'
                    else:
                        boat_data['orientation'] = 'horizontal'
                setattr(self, label, boat_data)
        self.ready = True
        self.save()


    def save(self, *args, **kwargs):
        if not self.pk:
            boats = Boat.objects.all()
            for boat in boats:
                data = {
                    'display': boat.data,
                    'status': 'active',
                    'coordinates': [],
                    'orientation': None
                }
                setattr(self, boat.data['label'], data)
        super(GamePlayerBoard, self).save(*args, **kwargs)


class Turn(models.Model):
    """ BoatFight Turn Model
        Stores information for each turn of each GamePlayer
    """
    gameplayer = models.ForeignKey(GamePlayer, on_delete=models.CASCADE)
    turn_index = models.IntegerField(default=1)
    status = models.CharField(
        max_length=10,
        choices=(
            ('pending', 'pending'),
            ('active', 'active'),
            ('over', 'over'),
        ),
        default='pending'
    )
    shots = models.JSONField(blank=True, default=[])

    def __str__(self):
        return '<Turn: {}> Player: {}'.format(self.turn_index, self.gameplayer)

    def end_turn(self, shots, hits):
        for shot in shots:
            shot_coordinates = [shot['x'], shot['y']]
            if shot_coordinates in hits:
                shot['status'] = 'hit'
            else:
                shot['status'] = 'missed'
            self.shots.append(shot)

        self.status = 'over'
        self.save()

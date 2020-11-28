from django.db import models

from bogames.models import Game, Player


class Boat(object):
    def __init__(self, label, units):
        self.label = label
        self.units = units


SHIPS = {
    'carrier': Boat('Carrier', 5),
    'battleship': Boat('Battleship', 4),
    'cruiser': Boat('Cruiser', 3),
    'submarine': Boat('Submarine', 3),
    'destroyer': Boat('Destroyer', 2),
}

class BoatFightGame(Game):

    def end_game(self):
        self.status = 'over'
        for gp in self.gameplayer_set.all():
            gp.turn_set.all().update(status='over')
            gp.is_current_player = False
            gp.save()
        self.save()

    @property
    def winner(self):
        for gp in self.gameplayer_set.all():
            if gp.available_shots > 0:
                return gp
        return None


class GamePlayer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(BoatFightGame, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=(
            ('challenged', 'challenged'),
            ('accepted', 'accepted'),
            ('ready', 'ready'),
        ),
        default='challenged'
    )
    is_current_player = models.BooleanField(default=False)

    @property
    def ships(self):
        return SHIPS

    @property
    def username(self):
        return self.player.username


    @property
    def available_shots(self):
        self.boatplacement.update_boat_status()
        boat_status_fields = [
            self.boatplacement.battleship_status,
            self.boatplacement.carrier_status,
            self.boatplacement.cruiser_status,
            self.boatplacement.submarine_status,
            self.boatplacement.destroyer_status
        ]
        available_shots = 0
        for field in boat_status_fields:
            if field == 'active':
                available_shots += 1
        return available_shots

    @property
    def current_turn(self):
        return self.turn_set.filter(status='active').first()

    def end_turn(self):
        if self.current_turn:
            self.current_turn.end_turn()

    def start_turn(self):
        GamePlayer.objects.filter(is_current_player=True).update(is_current_player=False)
        self.is_current_player = True
        self.save()
        new_turn_index = 1
        if self.current_turn:
            new_turn_index = self.current_turn + 1
            self.end_turn
        new_turn = Turn(
            gameplayer=self,
            turn_index=new_turn_index,
            status='active'
        )
        new_turn.save()
        return new_turn


class BoatPlacement(models.Model):
    STATUS_CHOICES = (
        ('active', 'active'),
        ('sunk', 'sunk')
    )
    player = models.OneToOneField(GamePlayer, on_delete=models.CASCADE)
    carrier_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    carrier_1_x = models.IntegerField(default=0)
    carrier_1_y = models.IntegerField(default=0)
    carrier_1_hit = models.BooleanField(default=False)
    carrier_2_x = models.IntegerField(default=0)
    carrier_2_y = models.IntegerField(default=0)
    carrier_2_hit = models.BooleanField(default=False)
    carrier_3_x = models.IntegerField(default=0)
    carrier_3_y = models.IntegerField(default=0)
    carrier_3_hit = models.BooleanField(default=False)
    carrier_4_x = models.IntegerField(default=0)
    carrier_4_y = models.IntegerField(default=0)
    carrier_4_hit = models.BooleanField(default=False)
    carrier_5_x = models.IntegerField(default=0)
    carrier_5_y = models.IntegerField(default=0)
    carrier_5_hit = models.BooleanField(default=False)

    battleship_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    battleship_1_x = models.IntegerField(default=0)
    battleship_1_y = models.IntegerField(default=0)
    battleship_1_hit = models.BooleanField(default=False)
    battleship_2_x = models.IntegerField(default=0)
    battleship_2_y = models.IntegerField(default=0)
    battleship_2_hit = models.BooleanField(default=False)
    battleship_3_x = models.IntegerField(default=0)
    battleship_3_y = models.IntegerField(default=0)
    battleship_3_hit = models.BooleanField(default=False)
    battleship_4_x = models.IntegerField(default=0)
    battleship_4_y = models.IntegerField(default=0)
    battleship_4_hit = models.BooleanField(default=False)

    cruiser_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    cruiser_1_x = models.IntegerField(default=0)
    cruiser_1_y = models.IntegerField(default=0)
    cruiser_1_hit = models.BooleanField(default=False)
    cruiser_2_x = models.IntegerField(default=0)
    cruiser_2_y = models.IntegerField(default=0)
    cruiser_2_hit = models.BooleanField(default=False)
    cruiser_3_x = models.IntegerField(default=0)
    cruiser_3_y = models.IntegerField(default=0)
    cruiser_3_hit = models.BooleanField(default=False)

    submarine_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    submarine_1_x = models.IntegerField(default=0)
    submarine_1_y = models.IntegerField(default=0)
    submarine_1_hit = models.BooleanField(default=False)
    submarine_2_x = models.IntegerField(default=0)
    submarine_2_y = models.IntegerField(default=0)
    submarine_2_hit = models.BooleanField(default=False)
    submarine_3_x = models.IntegerField(default=0)
    submarine_3_y = models.IntegerField(default=0)
    submarine_3_hit = models.BooleanField(default=False)

    destroyer_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    destroyer_1_x = models.IntegerField(default=0)
    destroyer_1_y = models.IntegerField(default=0)
    destroyer_1_hit = models.BooleanField(default=False)
    destroyer_2_x = models.IntegerField(default=0)
    destroyer_2_y = models.IntegerField(default=0)
    destroyer_2_hit = models.BooleanField(default=False)

    @property
    def coordinates(self):
        coordinates = {}
        for ship_label in SHIPS.keys():
            for i in range(1, 6):
                test_field_name = '{}_{}_x'.format(ship_label, i)
                if hasattr(self, test_field_name):
                    x_field_coord = getattr(self, '{}_{}_x'.format(ship_label, i))
                    y_field_coord = getattr(self, '{}_{}_y'.format(ship_label, i))
                    coordinates[(x_field_coord, y_field_coord)] = '{}_{}_hit'.format(ship_label, i)

        return coordinates

    @property
    def sunk_coordinates(self):
        coordinates = []
        for ship_label, boat in SHIPS.items():
            status_field = '{}_status'.format(ship_label)
            if getattr(self, status_field) == 'sunk':
                for i in range(1, boat.units + 1):
                    x_coordinate = getattr(self, '{}_{}_x'.format(ship_label, i))
                    y_coordinate = getattr(self, '{}_{}_y'.format(ship_label, i))
                    coordinates.append((x_coordinate, y_coordinate))
        return coordinates

    def check_hits(self, shots):
        boat_coordinates = self.coordinates
        hits = []
        for i in range(1, 6):
            y_coordinate = shots.get('shot_{}_y'.format(i))
            x_coordinate = shots.get('shot_{}_x'.format(i))
            hit_field = 'shot_{}_status'.format(i)
            if x_coordinate:
                coordinates = (x_coordinate, y_coordinate)
                if coordinates in boat_coordinates:
                    setattr(self, boat_coordinates[coordinates], True)
                    hits.append(hit_field)
        self.save()
        return hits

    def update_boat_status(self):
        for ship_label, boat in SHIPS.items():
            num_hits = 0
            status_field = '{}_status'.format(ship_label)
            ship_status = getattr(self, status_field)
            if ship_status == 'active':
                for i in range(1, boat.units + 1):
                    hit_field = '{}_{}_hit'.format(ship_label, i)
                    if getattr(self, hit_field) == True:
                        num_hits += 1
                if num_hits == boat.units:
                    status_field = '{}_status'.format(ship_label)
                    setattr(self, status_field, 'sunk')
        self.save()

    def sort_shots(self, turns, sunk_coordinates):
        shot_coordinates = {
            'hits': [],
            'misses': [],
            'sunk': []
        }

        for turn in turns:
            for i in range(1, 6):
                x_coordinate = getattr(turn, 'shot_{}_x'.format(i))
                y_coordinate = getattr(turn, 'shot_{}_y'.format(i))
                hit_field = 'shot_{}_status'.format(i)
                if (x_coordinate, y_coordinate) in sunk_coordinates:
                    shot_coordinates['sunk'].append((x_coordinate, y_coordinate))
                elif getattr(turn, hit_field) == 'hit':
                    shot_coordinates['hits'].append((x_coordinate, y_coordinate))
                elif getattr(turn, hit_field) == 'miss':
                    shot_coordinates['misses'].append((x_coordinate, y_coordinate))
        return shot_coordinates

    def get_opponent_shots(self, opponent):
        opponent_sunk_coordinates = self.sunk_coordinates
        return self.sort_shots(opponent.turn_set.all(), opponent_sunk_coordinates)

    def get_player_shots(self, opponent):
        player_sunk_coordinates = opponent.boatplacement.sunk_coordinates
        return self.sort_shots(self.player.turn_set.all(), player_sunk_coordinates)


class Turn(models.Model):
    SHOT_STATUS = [
        ('hit', 'hit'),
        ('miss', 'miss'),
        ('na', 'na')
    ]
    gameplayer = models.ForeignKey(GamePlayer, on_delete=models.CASCADE)
    turn_index = models.IntegerField(default=1)
    status = models.CharField(
        max_length=10,
        choices=(
            ('active', 'active'),
            ('over', 'over'),
        ),
        default='active'
    )
    shot_1_x = models.IntegerField(default=0)
    shot_1_y = models.IntegerField(default=0)
    shot_1_status = models.CharField(
        max_length=10,
        choices=SHOT_STATUS,
        default='na'
    )
    shot_2_x = models.IntegerField(default=0)
    shot_2_y = models.IntegerField(default=0)
    shot_2_status = models.CharField(
        max_length=10,
        choices=SHOT_STATUS,
        default='na'
    )
    shot_3_x = models.IntegerField(default=0)
    shot_3_y = models.IntegerField(default=0)
    shot_3_status = models.CharField(
        max_length=10,
        choices=SHOT_STATUS,
        default='na'
    )
    shot_4_x = models.IntegerField(default=0)
    shot_4_y = models.IntegerField(default=0)
    shot_4_status = models.CharField(
        max_length=10,
        choices=SHOT_STATUS,
        default='na'
    )
    shot_5_x = models.IntegerField(default=0)
    shot_5_y = models.IntegerField(default=0)
    shot_5_status = models.CharField(
        max_length=10,
        choices=SHOT_STATUS,
        default='na'
    )

    def end_turn(self):
        for i in range(1, 6):
            x_field = 'shot_{}_x'.format(i)
            shot_field = 'shot_{}_status'.format(i)
            had_shot = getattr(self, x_field)
            shot_status = getattr(self, shot_field)
            if had_shot > 0 and shot_status == 'na':
                setattr(self, shot_field, 'miss')
        self.status = 'over'
        self.save()


    def update(self, update_dict):
        for field, value in update_dict.items():
            setattr(self, field, value)
        self.save()

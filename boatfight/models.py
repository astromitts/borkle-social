from django.db import models

from bogames.models import Game, Player


class Boat(object):
    def __init__(self, label, units):
        self.label = label
        self.units = units
        self.image = 'images/boats/{}/{}.png'.format(label, label)
        self.image_map = []
        for i in range(1, self.units + 1):
            self.image_map.append('images/boats/{}/{}.png'.format(label, i))


SHIPS = {
    'longship': Boat('Longship', 5),
    'knarr': Boat('Knarr', 4),
    'karve': Boat('Karve', 3),
    'kraken': Boat('Kraken', 3),
    'faering': Boat('Faering', 2),
}


class BoatFightGame(Game):

    def __str__(self):
        return '<BoatFightGame: {}, CodeName: {}, UUID: {}>'.format(self.pk, self.code_name, self.uuid)

    def end_game(self):
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
        return self.gameplayer_set.get(status='won')

    def get_gameplayer(self, player):
        return self.gameplayer_set.filter(player=player).first()


class GamePlayer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(BoatFightGame, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=(
            ('challenged', 'challenged'),
            ('accepted', 'accepted'),
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
    def has_boatplacement(self):
        try:
            boatplacement = self.boatplacement
            return True
        except GamePlayer.boatplacement.RelatedObjectDoesNotExist:
            return False

    @property
    def available_shots(self):
        available_shots = 5
        try:
            available_shots = 0
            self.boatplacement.update_boat_status()
            boat_status_fields = [
                self.boatplacement.knarr_status,
                self.boatplacement.longship_status,
                self.boatplacement.karve_status,
                self.boatplacement.kraken_status,
                self.boatplacement.faering_status
            ]
            for field in boat_status_fields:
                if field == 'active':
                    available_shots += 1
        except GamePlayer.boatplacement.RelatedObjectDoesNotExist:
            pass
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
    longship_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    longship_1_x = models.IntegerField(default=0)
    longship_1_y = models.IntegerField(default=0)
    longship_1_hit = models.BooleanField(default=False)
    longship_2_x = models.IntegerField(default=0)
    longship_2_y = models.IntegerField(default=0)
    longship_2_hit = models.BooleanField(default=False)
    longship_3_x = models.IntegerField(default=0)
    longship_3_y = models.IntegerField(default=0)
    longship_3_hit = models.BooleanField(default=False)
    longship_4_x = models.IntegerField(default=0)
    longship_4_y = models.IntegerField(default=0)
    longship_4_hit = models.BooleanField(default=False)
    longship_5_x = models.IntegerField(default=0)
    longship_5_y = models.IntegerField(default=0)
    longship_5_hit = models.BooleanField(default=False)

    knarr_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    knarr_1_x = models.IntegerField(default=0)
    knarr_1_y = models.IntegerField(default=0)
    knarr_1_hit = models.BooleanField(default=False)
    knarr_2_x = models.IntegerField(default=0)
    knarr_2_y = models.IntegerField(default=0)
    knarr_2_hit = models.BooleanField(default=False)
    knarr_3_x = models.IntegerField(default=0)
    knarr_3_y = models.IntegerField(default=0)
    knarr_3_hit = models.BooleanField(default=False)
    knarr_4_x = models.IntegerField(default=0)
    knarr_4_y = models.IntegerField(default=0)
    knarr_4_hit = models.BooleanField(default=False)

    karve_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    karve_1_x = models.IntegerField(default=0)
    karve_1_y = models.IntegerField(default=0)
    karve_1_hit = models.BooleanField(default=False)
    karve_2_x = models.IntegerField(default=0)
    karve_2_y = models.IntegerField(default=0)
    karve_2_hit = models.BooleanField(default=False)
    karve_3_x = models.IntegerField(default=0)
    karve_3_y = models.IntegerField(default=0)
    karve_3_hit = models.BooleanField(default=False)

    kraken_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    kraken_1_x = models.IntegerField(default=0)
    kraken_1_y = models.IntegerField(default=0)
    kraken_1_hit = models.BooleanField(default=False)
    kraken_2_x = models.IntegerField(default=0)
    kraken_2_y = models.IntegerField(default=0)
    kraken_2_hit = models.BooleanField(default=False)
    kraken_3_x = models.IntegerField(default=0)
    kraken_3_y = models.IntegerField(default=0)
    kraken_3_hit = models.BooleanField(default=False)

    faering_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    faering_1_x = models.IntegerField(default=0)
    faering_1_y = models.IntegerField(default=0)
    faering_1_hit = models.BooleanField(default=False)
    faering_2_x = models.IntegerField(default=0)
    faering_2_y = models.IntegerField(default=0)
    faering_2_hit = models.BooleanField(default=False)

    def __str__(self):
        return '<BoatPlacement: {}> {}'.format(self.pk, self.player)

    def boat_orientation(self, boat_type):
        x_1_coordinate = getattr(self, '{}_1_x'.format(boat_type))
        x_2_coordinate = getattr(self, '{}_2_x'.format(boat_type))
        if x_1_coordinate == x_2_coordinate:
            return 'vertical'
        return 'horizontal'

    @property
    def longship_orientation(self):
        return self.boat_orientation('longship')

    @property
    def knarr_orientation(self):
        return self.boat_orientation('knarr')

    @property
    def karve_orientation(self):
        return self.boat_orientation('karve')

    @property
    def kraken_orientation(self):
        return self.boat_orientation('kraken')

    @property
    def faering_orientation(self):
        return self.boat_orientation('faering')


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

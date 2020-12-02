from django.db import models

from bogames.models import Game, GamePlayer

import json
import random


class BoxDotGame(Game):
    _data = models.TextField(blank=True, null=True)

    def __str__(self):
        return '<BoxDotGame: {}, CodeName: {}, UUID: {}>'.format(self.pk, self.code_name, self.uuid)

    @property
    def data(self):
        return json.loads(self._data)

    def update_board(self, xpos, ypos, gameplayer_id):
        current_data = self.data
        if not current_data.get('placedTiles'):
            current_data['placedTiles'] = []

        current_data['placedTiles'].append(
            {
                'x': xpos,
                'y': ypos,
                'filledById': gameplayer_id,
            }
        )
        current_data['placedTilesCount'] = len(current_data['placedTiles'])
        self._data = current_data
        self.save()

    def advance_player(self):
        current_player = self.gameplayer_set.filter(is_current_player=True).first()
        if not current_player:
             current_player = self.gameplayer_set.order_by('?').first()
        next_player = self.gameplayer_set.exclude(pk=current_player.pk).first()
        current_player.is_current_player = False
        current_player.save()

        next_player.is_current_player = True
        next_player.save()

    def save(self, *args, **kwargs):
        total_tiles = 7 * 6
        if self._data:
            if isinstance(self._data, dict):
                self._data = json.dumps(self._data)
            elif isinstance(self._data, str):
                # just run it through json.load to throw an error if it is malformed
                json.loads(self._data)
        else:
            self._data = json.dumps({'gameStatus': self.status, 'placedTilesCount': 0, 'totalTiles': total_tiles, 'placedTiles': [], 'winner': '', 'loser': '', 'winningCoordinates': []})
        super(BoxDotGame, self).save(*args, **kwargs)

    def end_game(self, winning_coordinates, winner, loser):
        winner.status = 'won'
        winner.save()
        loser.status = 'lost'
        loser.save()

        winning_coordinates_unique = []
        for coord in winning_coordinates:
            if not coord in winning_coordinates_unique:
                winning_coordinates_unique.append(coord)

        tmp_data = self.data
        _data = {}
        _data['gameStatus'] = 'over'
        _data['winner'] = winner.player.username
        _data['loser'] = loser.player.username
        _data['winningCoordinates'] = winning_coordinates_unique
        _data['placedTiles'] = tmp_data['placedTiles']
        self._data = _data
        self.status = 'over'
        self.save()

    def draw_game(self):
        for gp in self.gameplayer_set.all():
            gp.status = 'lost'
            gp.save()
        self.status = 'over'
        tmp_data = self.data
        tmp_data['gameStatus'] = 'over'
        self._data = tmp_data
        self.save()

    def start_game(self):
        self.status = 'active'
        first_player = random.choice(self.gameplayer_set.all())
        first_player.start_turn()
        tmp_data = self.data
        tmp_data['gameStatus'] = 'active'
        self._data = tmp_data
        self.save()


class GamePlayer(GamePlayer):
    game = models.ForeignKey(BoxDotGame, on_delete=models.CASCADE)
    @property
    def username(self):
        return self.player.username

    def start_turn(self):
        self.is_current_player = True
        self.save()


    def __str__(self):
        return '<GamePlayer: {} ({})> Game: {}'.format(self.pk, self.player.username, self.game.uuid)


class Turn(models.Model):
    gameplayer = models.ForeignKey(GamePlayer, on_delete=models.CASCADE)

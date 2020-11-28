from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.template import loader
from django.http import HttpResponse, JsonResponse

from boatfight.forms import InitializeGameForm

from bogames.models import Player
from bogames.views import DashboardBase

from boatfight.models import (
    SHIPS,
    BoatFightGame,
    GamePlayer,
    BoatPlacement,
    Turn,
)

class BoatFighterBase(View):
    def setup(self, request, *args, **kwargs):
        super(BoatFighterBase, self).setup(request, *args, **kwargs)
        self.player = Player.objects.get(user=request.user)


class BoatFighterGame(BoatFighterBase):
    def setup(self, request, *args, **kwargs):
        super(BoatFighterGame, self).setup(request, *args, **kwargs)
        self.game = BoatFightGame.objects.get(uuid=kwargs['game_uuid'])
        self.boatfighter = GamePlayer.objects.get(player=self.player)
        self.opponent = self.game.gameplayer_set.exclude(player=self.boatfighter.player).first()
        self.boatplacement = BoatPlacement.objects.filter(player=self.boatfighter).first()
        self.is_current_player = self.boatfighter.is_current_player


class Dashboard(DashboardBase):
    def setup(self, request, *args, **kwargs):
        super(BorkleDashboard, self).setup(request, *args, **kwargs)
        self.refresh_url = reverse('borkle_dashboard_api')


class InitializeGame(BoatFighterBase):
    def setup(self, request, *args, **kwargs):
        super(InitializeGame, self).setup(request, *args, **kwargs)
        self.formClass = InitializeGameForm
        self.template = loader.get_template('bogames/generic_form.html')

    def get(self, request, *args, **kwargs):
        form = self.formClass(
            initial={
                'initializing_player_id': self.player.pk
            }
        )
        context = {
            'form': form,
            'form_header': 'Start a boat fight!'
        }
        return HttpResponse(self.template.render(context, request))

    def post(self, request, *args, **kwargs):
        form = self.formClass(request.POST)
        if form.is_valid():
            players = [
                self.player,
                Player.get_by_username(request.POST['opponent'])
            ]
            game = BoatFightGame.initialize_game(players, GamePlayer)
            return redirect(reverse('boatfight_game', kwargs={'game_uuid': game.uuid}))
        context = {
            'form': form,
            'form_header': 'Start a boat fight!'
        }
        return HttpResponse(self.template.render(context, request))


class GameBoard(BoatFighterGame):
    def get(self, request, *args, **kwargs):
        if self.boatplacement:
            template = loader.get_template('boatfight/boatfight.html')
            self.game.set_status()
            available_shots = self.boatfighter.available_shots
        else:
            template = loader.get_template('boatfight/boatfight_placement_board.html')
            available_shots = 0

        context = {
            'x_axis': range(1, 11),
            'y_axis': range(1, 11),
            'boats_to_place': SHIPS,
            'game': self.game,
            'available_shots': available_shots,
        }
        return HttpResponse(template.render(context, request))

    def post(self, request, *args, **kwargs):
        boat_placement_data = {field: int(value) for field, value in request.POST.items()}
        boat_placement_data.update({'player_id': self.boatfighter.pk})
        boat_placement = BoatPlacement(**boat_placement_data)
        boat_placement.save()
        self.boatfighter.status = 'ready'
        self.boatfighter.save()
        return JsonResponse({
            'status': 'success',
        })


class BoatFightApi(BoatFighterGame):
    def _player(self, player):
        return {
            'playerName': player.username,
            'isCurrentPlayer': player.is_current_player,
            'availableShots': player.available_shots
        }

    def _opponent(self):
        return self._player(self.opponent)

    def get(self, request, *args, **kwargs):
        data = {
            'is_current_player': self.is_current_player,
            'player': self._player(self.boatfighter),
            'opponent': self._opponent(),
            'gameStatus': self.game.status,
        }

        if self.boatfighter.available_shots == 0 or self.opponent.available_shots == 0:
            self.game.end_game()
            data.update({'winner': self.game.winner.username})

        if kwargs['api_target'] == 'boardsetup':
            data.update({
                'boats': {
                    'battleship': {'positions': []},
                    'carrier': {'positions': []},
                    'submarine': {'positions': []},
                    'cruiser': {'positions': []},
                    'destroyer': {'positions': []},
                }
            })
            for boat_type in data['boats'].keys():
                for i in range(1, 6):
                    xfield = '{}_{}_x'.format(boat_type, i)
                    yfield = '{}_{}_y'.format(boat_type, i)
                    if hasattr(self.boatplacement, xfield):
                        position = {
                            'xPos': getattr(self.boatplacement, xfield),
                            'yPos': getattr(self.boatplacement, yfield)
                        }
                        data['boats'][boat_type]['positions'].append(position)
        elif kwargs['api_target'] == 'gamestatus':
            opponent_shots = self.boatfighter.boatplacement.get_opponent_shots(self.opponent)
            get_player_shots = self.boatfighter.boatplacement.get_player_shots(self.opponent)
            data.update(
                {
                    'opponentShots': opponent_shots,
                    'playerShots': get_player_shots,
                }
            )
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        if kwargs['api_target'] == 'fire':
            post_data = {field: int(value) for field, value in request.POST.items()}
            self.boatfighter.current_turn.update(post_data)
            hits = self.opponent.boatplacement.check_hits(post_data)
            hit_data = {field: 'hit' for field in hits}
            self.boatfighter.current_turn.update(hit_data)
            self.boatfighter.end_turn()
            self.opponent.start_turn()
            data = {
                'status': 'success'
            }
        return JsonResponse(data)

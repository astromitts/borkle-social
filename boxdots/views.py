from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.views import View
from django.template import loader
from django.http import HttpResponse, JsonResponse

from bogames.models import Player
from bogames.views import (
    DashboardBase,
    DashBoardDataGameBase,
    DeclineGameView,
    BoGameBase,
    JoinGameView,
    CancelGameView,
    LeaveGameView,
)
from boxdots.forms import InitializeGameForm
from bogames.models import DataGame
from boxdots.models import (
    BoxDotDataGame as BoxDotGame,
    GamePlayer,
)
import json


class BoxDotBaseView(BoGameBase):
    def setup(self, request, *args, **kwargs):
        super(BoxDotBaseView, self).setup(request, *args, **kwargs)
        self.game_path = 'boxdots_game'
        self.cancel_path = 'boxdots_game_cancel'
        self.join_path = 'boxdots_game_accept_invitation_link'
        self.decline_path = 'boxdots_game_decline_invitation_link'
        self.dashboard_refresh_url = 'boxdots_dashboard_api'
        self.start_game_path = 'boxdots_start'
        self.dashboard_path = 'boxdots_dashboard'
        self.template_base = 'boxdots/base.html'
        self.gamePlayerClass = GamePlayer

        if request.user.is_authenticated:
            self.player = Player.get_or_create(user=self.request.user)
            request.session['player_id'] = self.player.pk
            if 'game_uuid' in kwargs:
                try:
                    self.game = BoxDotGame.objects.filter(uuid=kwargs['game_uuid']).first()
                except ValidationError:
                    self.game = None

                if self.game:
                    self.gameplayer = GamePlayer.objects.filter(game=self.game, player=self.player).first()
                    self.opponent = self.game.gameplayer_set.exclude(player=self.gameplayer.player).first()
                    if self.game.all_players_ready and self.game.status in ['waiting', 'pending']:
                        self.game.start_game()

    def get_game(self, uuid):
        return DataGame.objects.get(uuid=uuid)


class Dashboard(BoxDotBaseView, DashboardBase):
    def setup(self, request, *args, **kwargs):
        super(Dashboard, self).setup(request, *args, **kwargs)
        self.refresh_url = reverse('borkle_dashboard_api')


class DashboardApi(BoxDotBaseView, DashBoardDataGameBase):
    pass

class InitializeGame(BoxDotBaseView):
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
            'form_header': 'Start a Box Dot game!',
            'base_template': self.template_base,
        }
        return HttpResponse(self.template.render(context, request))

    def post(self, request, *args, **kwargs):
        form = self.formClass(request.POST)
        if form.is_valid():
            opponent = Player.get_by_username(request.POST['opponent'])
            players = [
                self.player,
                opponent,
            ]

            game = BoxDotGame.initialize_game(players, GamePlayer)
            game.created_by = self.player
            game.save()
            initializing_gameplayer = GamePlayer.objects.get(game=game, player=self.player)
            initializing_gameplayer.set_status('ready')
            initializing_gameplayer.save()
            return redirect(reverse('boxdots_game', kwargs={'game_uuid': game.uuid}))
        context = {
            'form': form,
            'form_header': 'Start a Box Dot game!',
            'base_template': self.template_base,
        }
        return HttpResponse(self.template.render(context, request))


class JoinGame(BoxDotBaseView, JoinGameView):
    pass


class CancelGame(BoxDotBaseView, CancelGameView):
    pass


class LeaveGame(BoxDotBaseView, LeaveGameView):
    pass


class DeclineGame(BoxDotBaseView, DeclineGameView):
    pass


class BoxDotGameView(BoxDotBaseView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('boxdots/gameboard.html')
        if self.gameplayer.data['status'] == 'waiting':
            self.gameplayer.data['status'] = 'ready'
            self.gameplayer.save()

        context = {
            'game': self.game,
            'gameplayer': self.gameplayer,
            'x_axis': range(1, 8),
            'y_axis': range(1, 7),
        }
        return HttpResponse(template.render(context, request))


class BoxDotGameApi(BoxDotBaseView):
    def get(self, request, *args, **kwargs):
        if kwargs['api_target'] == 'getboard':
            player_set = self.game.get_player_set(self.gameplayer)
            data = {
                'metaData': self.game.meta,
                'gameData': self.game.data,
                'localPlayer': player_set['player'],
                'opponentPlayer': player_set['opponent'],
            }
            return JsonResponse(data)


    def post(self, request, *args, **kwargs):
        if kwargs['api_target'] == 'updateboard':
            xpos = request.POST['x']
            ypos = request.POST['y']
            gameplayer_id = request.POST['gameplayer_id']
            self.game.update_board(xpos, ypos, gameplayer_id)
            self.game.advance_player(self.gameplayer, self.opponent)
            return JsonResponse(self.game.data)
        elif kwargs['api_target'] == 'endgame':
            coords = json.loads(request.POST['coordinates'])
            self.game.end_game(
                winning_coordinates=coords['coordinates'],
                winner=self.gameplayer,
                loser=self.opponent,
            )
            return JsonResponse(self.game.data)
        elif kwargs['api_target'] == 'drawgame':
            self.game.draw_game()
            return JsonResponse(self.game.data)



from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.template import loader
from django.http import HttpResponse, JsonResponse

from bogames.models import Player, Game
from borkle.models import GamePlayer


class BoGameBase(View):
    def setup(self, request, *args, **kwargs):
        super(BoGameBase, self).setup(request, *args, **kwargs)
        self.player = Player.objects.get(user=request.user)
        self.game_path = 'ERROR'
        self.cancel_path = 'ERROR'
        self.join_path = 'ERROR'
        self.decline_path = 'ERROR'
        self.leave_game_path = 'ERROR'
        self.dashboard_path = 'ERROR'
        self.dashboard_refresh_url = 'ERROR'
        self.dashboard_api_js_file = 'js/borkle/dashboardApi.js'
        self.gamePlayerClass = GamePlayer

        if kwargs.get('game_uuid'):
            self.game = Game.objects.get(uuid=kwargs['game_uuid'])


class LandingPage(BoGameBase):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('bogames/landing.html')
        context = {
            'games': {
                'Borkle': reverse(self.dashboard_path)
            }
        }
        return HttpResponse(template.render(context, request))


class DashboardBase(BoGameBase):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('bogames/dashboard.html')
        context = {
            'player': self.player,
            'dashboard_refresh_url': self.dashboard_refresh_url,
            'dashboard_api_js_file': self.dashboard_api_js_file,
        }
        return HttpResponse(template.render(context, request))


class DashboardApiBase(BoGameBase):

    def _format_player(self, player, current_player):
        return {
            'username': player.username,
            'ready': player.status == 'ready',
            'status': player.status,
            'isCurrentPlayer': player == current_player,
        }

    def _add_formatted_games(self, games, append_to_list, status):
        for game in games:
            player_gameplayer = game.get_gameplayer(self.player)
            if game.current_player and game.current_player.current_turn:
                current_game_player = game.current_player.username
                is_current_player = game.current_player.current_turn == player_gameplayer
            else:
                current_game_player = None
                is_current_player = False
            if hasattr(game, 'game_type'):
                game_type = game.game_type
                is_practice = game.game_type == 'practice'
            else:
                game_type = None
                is_practice = False

            append_to_list.append({
                'dashboardStatus': status,
                'uuid': game.uuid,
                'codeName': game.code_name,
                'createdBy': game.created_by.username,
                'isGameOwner': game.created_by == self.player,
                'current_player_name': current_game_player,
                'players': [self._format_player(gp, game.current_player) for gp in game.gameplayer_set.all()],
                'isCurrentPlayer': is_current_player,
                'isPracticeGame': is_practice,
                'gameType': game_type,
                'link': reverse(self.game_path, kwargs={'game_uuid': game.uuid}),
                'cancelLink': reverse(self.cancel_path, kwargs={'game_uuid': game.uuid}),
                'joinLink': reverse(self.join_path, kwargs={'game_uuid': game.uuid}),
                'declineLink': reverse(self.decline_path, kwargs={'game_uuid': game.uuid})
            })
        return append_to_list

    def get(self, request, *args, **kwargs):
        player_instances = self.gamePlayerClass.objects.filter(player=self.player)
        player_games = {
            'active': [],
            'pending': [],
            'invitations': [],
        }

        for player_inst in player_instances:
            game = player_inst.game
            if game.all_players_ready:
                player_games['active'].append(game)
            elif player_inst.ready:
                player_games['pending'].append(game)
            else:
                player_games['invitations'].append(game)

        data = {
            'playerName': self.player.username,
            'games': [],
        }
        data['games'] = self._add_formatted_games(player_games['active'], data['games'], 'active')
        data['games'] = self._add_formatted_games(player_games['pending'], data['games'], 'pending')
        data['games'] = self._add_formatted_games(player_games['invitations'], data['games'], 'invited')
        return JsonResponse(data)


class JoinGameView(BoGameBase):
    def get(self, request, *args, **kwargs):
        self.player.join_game(self.game, self.gamePlayerClass)
        if self.game.all_players_ready:
            self.game.start_game()
        return redirect(reverse(self.game_path, kwargs={'game_uuid': self.game.uuid}))


class DeclineGameView(BoGameBase):
    def get(self, request, *args, **kwargs):
        self.player.decline_game(self.game, self.gamePlayerClass)
        return redirect(reverse(self.dashboard_path))


class CancelGameView(View):
    def get(self, request, *args, **kwargs):
        if self.game.created_by == self.player:
            if request.GET.get('src', '') == 'game':
                cancel_url = reverse(self.game_path, kwargs={'game_uuid': self.game.uuid})
            else:
                cancel_url = reverse(self.dashboard_path)

            template = loader.get_template('borkle/confirm_action.html')
            context = {
                'cancel_url': cancel_url,
                'form_header': 'Are you sure you want to cancel the game?'
            }
            return HttpResponse(template.render(context, request))
        else:
            messages.error(request, 'Permission denied. Contact game owner for help.')

    def post(self, request, *args, **kwargs):
        if self.game.created_by == self.player:
            messages.success(request, 'Game cancelled.')
            self.game.delete()
        else:
            messages.error(request, 'Permission denied. Contact game owner for help.')
        return redirect(reverse(self.dashboard_path))


class LeaveGameView(View):

    def get(self, request, *args, **kwargs):
        template = loader.get_template('bogames/confirm_action.html')
        context = {
            'cancel_url': reverse(self.game_path, kwargs={'game_uuid': self.game.uuid}),
            'form_header': 'Are you sure you want to leave the game?'
        }
        return HttpResponse(template.render(context, request))

    def post(self, request, *args, **kwargs):
        self.game.boot_player(self.gameplayer)
        messages.success(request, 'Successfully left game.')
        if self.game.gameplayer_set.count() == 0:
            self.game.delete()
        return redirect(reverse(self.dashboard_path))

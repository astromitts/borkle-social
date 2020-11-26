from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.template import loader
from django.http import HttpResponse, JsonResponse

from borkle.models import Game, ScoreSet
from borkle.views import BorkleBaseView
from session_manager.views import AuthenticatedView
from borkle.utils import get_dice_image_path


class GameStatusApi(BorkleBaseView):
    def _scoreboard(self):
        scoreboard = []

        for player in self.game.gameplayer_set.all():
            scoreboard.append(
                {
                    'pk': player.pk,
                    'username': player.username,
                    'score': player.total_score,
                    'current_player': player == self.game.current_player,
                    'ready': player.ready,
                }
            )
        return scoreboard

    def _players_name_list(self):
        return [player.username for player in self.game.gameplayer_set.all()]

    def _format_scoresets(self, scoresets):
        formatted_scoresets = []
        for scoreset in scoresets:
            scoreset_data = {
                'scoreValue': scoreset.score,
                'scoreType': scoreset.score_type,
                'locked': scoreset.locked,
                'scorableValues': scoreset.scorable_values,
                'scorableFields': scoreset.scorable_fields,
                'scoreSetPk': scoreset.pk,
            }
            if scoreset.score == 0:
                scoreset_data['scoreable_value_images'] = ['0', ]
            formatted_scoresets.append(scoreset_data)
        return formatted_scoresets

    def _turnhistory(self, latest_turn=0):
        # turns = self.game.turn_set.filter(turn_index__gte=latest_turn).all()
        turn_history = []

        for player in self.game.gameplayer_set.all():
            player_data = {
                'username': player.username,
                'pk': player.pk,
                'turns': []
            }

            turns = player.turn_set.filter(active=False).filter(turn_index__gte=latest_turn).order_by('turn_index').all()
            for turn in turns:
                formatted_scoresets = self._format_scoresets(turn.scoreset_set.filter(locked=True).order_by('-pk').all())
                turn_data = {
                    'turn_index': turn.turn_index,
                    'score': str(turn.score),
                    'scoresets': formatted_scoresets,
                }
                player_data['turns'].append(turn_data)
            turn_history.append(player_data)

        return turn_history

    def _diceinfo(self, dice_value):
        return {
            'value': dice_value,
            'image': get_dice_image_path(dice_value)
        }

    def _diceboard(self):
        current_turn = self.game.current_player.current_turn
        data = {
            'is_current_player': self.is_current_player,
            'current_player': self.game.current_player.username,
            'current_score': current_turn.current_score,
            'available_dice_count': current_turn.available_dice_count,
            'last_turn': self.game.last_turn and not self.game.current_player.had_last_turn,
            'scoresets': self._format_scoresets(current_turn.scoreset_set.order_by('pk').all()),
            'rolledValues': current_turn.scorable_values,
            'scoredFields': current_turn.scorable_fields
        }
        return data

    def _players(self):
        players = []
        for player in self.game.gameplayer_set.all():
            players.append(
                {
                    'pk': player.pk,
                    'username': player.username,
                    'current_score': player.total_score,
                    'last_turn': self.game.last_turn and not player.had_last_turn
                }
            )
        return players

    def _player_scorecards(self):
        player_cards = {}
        players = self.game.gameplayer_set.all()
        for i in range(self.game.gameplayer_set.count()):
            player = players[i]

            if i != self.game.gameplayer_set.count() - 1:
                next_player_card = players[i + 1].username
            else:
                next_player_card = players[0].username

            if i != 0:
                previous_player_card = players[i - 1].username
            else:
                previous_player_card = players[self.game.gameplayer_set.count() - 1].username

            player_cards[player.username] = {
                'next_player_card': next_player_card,
                'previous_player_card': previous_player_card,
            }
        return player_cards


    def _format_winner(self):
        winners = self.game.winner
        data = {
            'winner_count': winners.count(),
            'winners': [{'username': w.username, 'score': w.total_score} for w in winners]
        }
        return data

    def get(self, request, *args, **kwargs):
        if not self.game:
            data = {'error': 'Game not found'}
            return JsonResponse(data, status=404)
        if not self.gameplayer:
            data = {'error': "Player is not in that game"}
            return JsonResponse(data, status=404)

        if kwargs['api_target'] == 'gameinfo':
            if self.game.status == 'over':
                data = {
                    'game_status': self.game.status,
                    'winners': self._format_winner(),
                }
            elif self.game.all_players_ready:
                data = {
                    'game_status': self.game.status,
                    'practice_game': self.game.game_type == 'practice',
                    'is_current_player': self.is_current_player,
                    'last_turn': self.game.last_turn,
                    'current_player': {
                        'player_id': self.game.current_player.pk,
                        'player_name': self.game.current_player.username,
                        'last_turn': self.game.last_turn,
                    },
                    'current_rolled_dice': self._diceboard(),
                    'current_score_sets': self._format_scoresets(self.game.current_player.current_turn.scoreset_set.order_by('-pk').all()),
                    'available_dice_count': self.game.current_player.current_turn.available_dice_count,
                }
            else:
                data = {
                    'game_status': self.game.status,
                    'practice_game': self.game.game_type == 'practice',
                    'player_names': self._scoreboard()
                }

        elif kwargs['api_target'] == 'scorecardsetup':
            data = {'scorecards': self._player_scorecards()}

        elif kwargs['api_target'] == 'scoreboard':
            data = {'scoreboard': self._scoreboard(), 'player_names': self._players_name_list()}
        elif kwargs['api_target'] == 'scorecard':
            if request.GET.get('latest_turn'):
                latest_turn = int(request.GET['latest_turn'])
            else:
                latest_turn = 0
            data = {'players': self._turnhistory(latest_turn)}
        elif kwargs['api_target'] == 'diceboard':
            data = self._diceboard()
        else:
            data = {
                'status': 'error',
                'message': 'Unrecognized request.'
            }

        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        if not self.game:
            data = {'error': 'Game not found'}
            return JsonResponse(data, status=404)
        if not self.gameplayer:
            data = {'error': "Player is not in that game"}
            return JsonResponse(data, status=404)

        data = {}
        if kwargs['api_target'] == 'scoredice':
            if self.is_current_player:
                dice_value_fields = []
                for field in request.POST.keys():
                    if field.startswith('rolled_dice'):
                        dice_value_fields.append(field)
                self.game.current_player.current_turn.make_selection(dice_value_fields)
                data = {
                    'status': 'success',
                }
            else:
                data = {
                    'status': 'error',
                    'message': "Hey! It's not your turn!"
                }
        elif kwargs['api_target'] == 'undoselection':
            scoreset_id = request.POST['scoreset_pk']
            scoreset = ScoreSet.objects.filter(pk=scoreset_id).first()
            if scoreset and not scoreset.locked:
                score_selection = self.game.current_player.current_turn.undo_score_selection(request.POST['scoreset_pk'])
                data = {
                    'status': 'success',
                    'current_rolled_dice': self._diceboard(),
                }
                data['current_rolled_dice'].update({'is_current_player': True})
            else:
                data = {
                    'status': 'error',
                    'message': 'scoreset not found or locked',
                }

        elif kwargs['api_target'] == 'endturn':
            if self.is_current_player:
                self.game.advance_player()
                data = {
                    'status': 'success'
                }
            else:
                data = {
                    'status': 'error',
                    'message': "Hey! It's not your turn!"
                }
        elif kwargs['api_target'] == 'rolldice':
            dice_vals = {}
            for i in range(0, 6):
                dice_val = request.POST.get('rolled_dice_{}'.format(i), None)
                dice_vals['rolled_dice_{}_value'.format(i + 1)] = dice_val
            if self.is_current_player:
                self.game.current_player.current_turn.set_roll_dice(dice_vals);
        elif kwargs['api_target'] == 'borkle':
            self.game.current_player.current_turn.borkle_turn()
            data = {
                'status': 'success'
            }
        else:
            data = {
                'status': 'error',
                'message': 'Unrecognized request.'
            }
        return JsonResponse(data)


class GameBoardApiVersion(BorkleBaseView):

    def get(self, request, *args, **kwargs):
        if not self.game:
            messages.error(request, 'Game not found')
            return redirect(reverse('dashboard'))
        if not self.gameplayer:
            messages.error(request, "You're not in that game")
            return redirect(reverse('dashboard'))

        template = loader.get_template('borkle/api_gameboard.html')
        rolled_dice_cache = []
        scored_dice_cache = []
        for i in range(0, 7):
            rolled_dice_cache.append('<img src="{}" class="rolled-dice" data-value="{}" id="rolled-dice-cache_{}" />'.format(get_dice_image_path(i), i, i))
            scored_dice_cache.append('<img src="{}" class="scored-dice" data-value="{}" id="scored-dice-cache_{}" />'.format(get_dice_image_path(i), i, i))
        context = {
            'game': self.game,
            'gameplayer': self.gameplayer,
            'rolled_dice_cache': rolled_dice_cache,
            'scored_dice_cache': scored_dice_cache,
            'is_game_owner': self.game.created_by == self.player
        }
        return HttpResponse(template.render(context, request))

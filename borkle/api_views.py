from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, JsonResponse

from borkle.models import ScoreSet
from borkle.views import BorkleProtectedGameView
from borkle.utils import get_dice_image_path


class GameStatusApi(BorkleProtectedGameView):
    def _scoreboard(self):
        scoreboard = []

        for player in self.game.gameplayer_set.all():
            scoreboard.append(
                {
                    'pk': player.pk,
                    'username': player.username,
                    'score': player.total_score,
                    'current_player': player == self.game.current_player
                }
            )
        return scoreboard

    def _players_name_list(self):
        return [player.username for player in self.game.gameplayer_set.all()]

    def _format_scoresets(self, scoresets):
        formatted_scoresets = []
        for scoreset in scoresets:
            scoreset_data = {
                'score': scoreset.score,
                'score_type': scoreset.score_type,
                'scoreable_value_images': [str(val) for val in scoreset.scorable_values],
                'locked': scoreset.locked,
                'pk': scoreset.pk,
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
            'available_score': self.game.current_player.current_turn.has_score,
            'last_turn': self.game.last_turn and not self.game.current_player.had_last_turn,
            'scoresets': self._format_scoresets(current_turn.scoreset_set.order_by('-pk').all()),
            'rolled_dice_1_value': self._diceinfo(current_turn.rolled_dice_1_value),
            'rolled_dice_2_value': self._diceinfo(current_turn.rolled_dice_2_value),
            'rolled_dice_3_value': self._diceinfo(current_turn.rolled_dice_3_value),
            'rolled_dice_4_value': self._diceinfo(current_turn.rolled_dice_4_value),
            'rolled_dice_5_value': self._diceinfo(current_turn.rolled_dice_5_value),
            'rolled_dice_6_value': self._diceinfo(current_turn.rolled_dice_6_value),
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

    def _format_winner(self):
        winners = self.game.winner
        data = {
            'winner_count': winners.count(),
            'winners': [{'username': w.username, 'score': w.total_score} for w in winners]
        }
        return data

    def get(self, request, *args, **kwargs):
        if kwargs['api_target'] == 'gameinfo':
            if self.game.status == 'over':
                data = {
                    'game_over': self.game.status == 'over',
                    'winners': self._format_winner(),
                }
            else:
                has_rolled = self.game.current_player.current_turn.has_rolled == True
                borkled = self.game.current_player.current_turn.borkle

                data = {
                    'game_over': self.game.status == 'over',
                    'is_current_player': self.is_current_player,
                    'last_turn': self.game.last_turn and not self.gameplayer.had_last_turn,
                    'borkled': borkled,
                    'current_player': {
                        'player_id': self.game.current_player.pk,
                        'player_name': self.game.current_player.username,
                    },
                    'current_rolled_dice': self._diceboard(),
                    'current_score_sets': self._format_scoresets(self.game.current_player.current_turn.scoreset_set.order_by('-pk').all()),
                    'can_end_turn': self.game.current_player.current_turn.can_end_turn,
                    'can_roll': self.game.current_player.current_turn.can_roll,
                    'available_dice_count': self.game.current_player.current_turn.available_dice_count,
                }
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
        data = {}
        if kwargs['api_target'] == 'scoredice':
            if self.is_current_player:
                dice_value_fields = []
                for field in request.POST.keys():
                    if field.startswith('rolled_dice'):
                        dice_value_fields.append(field)
                has_score = self.game.current_player.current_turn.check_score(dice_value_fields)
                if not has_score:
                    data = {
                        'status': 'error',
                        'message': 'Not a scoring set. Try something else.'
                    }
                else:
                    self.game.current_player.current_turn.make_selection(dice_value_fields)
                    scoresets = self._format_scoresets(self.game.current_player.current_turn.scoreset_set.order_by('-pk').all())
                    data = {
                        'status': 'success',
                        'scoresets': scoresets,
                        'available_dice_count': self.game.current_player.current_turn.available_dice_count,
                        'can_select_more': self.game.current_player.current_turn.has_score,
                        'turn_score': self.game.current_player.current_turn.current_score,
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
            if self.is_current_player:
                self.gameplayer.roll_dice()
                data = self._diceboard()
        else:
            data = {
                'status': 'error',
                'message': 'Unrecognized request.'
            }
        return JsonResponse(data)


class GameBoardApiVersion(BorkleProtectedGameView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('borkle/api_gameboard.html')
        rolled_dice_cache = []
        scored_dice_cache = []
        for i in range(0, 7):
            rolled_dice_cache.append('<img src="{}" class="rolled-dice" id="rolled-dice-cache_{}" />'.format(get_dice_image_path(i), i))
            scored_dice_cache.append('<img src="{}" class="scored-dice" id="scored-dice-cache_{}" />'.format(get_dice_image_path(i), i))
        context = {
            'game': self.game,
            'gameplayer': self.gameplayer,
            'rolled_dice_cache': rolled_dice_cache,
            'scored_dice_cache': scored_dice_cache,
            'is_game_owner': self.game.created_by == self.player
        }
        return HttpResponse(template.render(context, request))

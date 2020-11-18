from django.forms import (
    Form,
    IntegerField,
    CharField,
    HiddenInput
)
from django.core.exceptions import ValidationError
from borkle.models import Player


def _validate_player(player_username):
    if player_username:
        player = Player.get_by_username(username=player_username)
        if not player:
            return False
    return True


class InitializePracticeGameForm(Form):
    how_many_points_are_you_playing_to = IntegerField()


class InitializeGameForm(Form):
    how_many_points_are_you_playing_to = IntegerField()
    initializing_player_id = IntegerField(widget=HiddenInput())
    player_1 = CharField(required=False)
    player_2 = CharField(required=False)
    player_3 = CharField(required=False)
    player_4 = CharField(required=False)
    player_5 = CharField(required=False)

    player_field_label = 'Player username'
    player_1.label = player_field_label
    player_2.label = player_field_label
    player_3.label = player_field_label
    player_4.label = player_field_label
    player_5.label = player_field_label

    class Meta:
        widgets = {
            'initializing_player_id': HiddenInput(),
        }

    def clean_player_1(self):
        data = self.cleaned_data['player_1']
        if not _validate_player(data):
            raise ValidationError('Player not found.')
        return data

    def clean_player_2(self):
        data = self.cleaned_data['player_2']
        if not _validate_player(data):
            raise ValidationError('Player not found.')
        return data

    def clean_player_3(self):
        data = self.cleaned_data['player_3']
        if not _validate_player(data):
            raise ValidationError('Player not found.')
        return data

    def clean_player_4(self):
        data = self.cleaned_data['player_4']
        if not _validate_player(data):
            raise ValidationError('Player not found.')
        return data

    def clean_player_5(self):
        data = self.cleaned_data['player_5']
        if not _validate_player(data):
            raise ValidationError('Player not found.')
        return data

    def clean(self):
        super(InitializeGameForm, self).clean()
        data = self.cleaned_data
        required_one_of_fields = ['player_1', 'player_2', 'player_3', 'player_4', 'player_5']
        has_at_least_one_required = False
        initializing_player = Player.objects.get(pk=data['initializing_player_id'])
        for required_one_of in required_one_of_fields:
            if data.get(required_one_of) != '':
                has_at_least_one_required = True
                invitee = Player.get_by_username(username=data.get(required_one_of))
                if initializing_player == invitee:
                    raise ValidationError("You can't invite yourself, you are invited by default when you create a game!")
        if not has_at_least_one_required:
            raise ValidationError('You must invite at least one other player.')
        return data

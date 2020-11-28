from django.forms import (
    Form,
    IntegerField,
    CharField,
    HiddenInput
)
from django.core.exceptions import ValidationError
from bogames.form_utils import _validate_player
from bogames.models import Player


class InitializeGameForm(Form):
    initializing_player_id = IntegerField(widget=HiddenInput())
    opponent = CharField(required=False)

    class Meta:
        widgets = {
            'initializing_player_id': HiddenInput(),
        }

    def clean_opponent(self):
        data = self.cleaned_data['opponent']
        initializing_player_id = self.cleaned_data['initializing_player_id']
        initializing_player = Player.objects.get(pk=initializing_player_id)
        (player_found, player_not_initializer) = _validate_player(data, initializing_player)
        if not player_found:
            raise ValidationError('Player not found.')
        if not player_not_initializer:
            raise ValidationError("You can't invite yourself, you are invited by default when you create a game!")
        return data

    # def clean(self):
    #     super(InitializeGameForm, self).clean()
    #     data = self.cleaned_data
    #     initializing_player = Player.objects.get(pk=data['initializing_player_id'])
    #     import pdb
    #     pdb.set_trace()
    #     invitee = Player.get_by_username(username=data['opponent'])
    #     if initializing_player == invitee:
    #         raise ValidationError("You can't invite yourself, you are invited by default when you create a game!")
    #     return data

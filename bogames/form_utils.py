from bogames.models import Player


def _validate_player(player_username, initializing_player=None):
    if player_username:
        player = Player.get_by_username(username=player_username)
        if not player:
            if initializing_player:
                return (False, True)
            return False
    if initializing_player:
        if player == initializing_player:
            return (False, False)
        return (True, True)
    return True

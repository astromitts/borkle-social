$(document).ready(function playGame(){
	// Just turn off the refresh is the game is over
	var data = checkGameData(false);
	if ( data['game_over'] ) {
		var autorefresh = false;
		displayWinner(data['winners']);
	} else {
		var autorefresh = true;
		bindRollDice();
		bindScoreDice();
		bindEndTurn();
	}
	// Set game play functions to refresh
	autorefresh = true;
	var currentPlayerTriggered = false;
	if (autorefresh) {
		window.setInterval(function(){

			var needsInitiateTurn = false;
			var refreshGameInfoUrl = $('input#api-gameinfo-url').val();
			var resultData = {};
			$.ajax({
				method: 'GET',
				url: refreshGameInfoUrl,
				dataType: 'json',
				success: function setData(data) {
					resultData = data;
					var isCurrentPlayer = data['is_current_player'];
					if (isCurrentPlayer) {
						if (!currentPlayerTriggered) {
							refreshScoreboard();
							initiateTurn();
							currentPlayerTriggered = true;
						}
					} else {
						currentPlayerTriggered = false;
					}
				}
			});

		}, 1000)
	}
});
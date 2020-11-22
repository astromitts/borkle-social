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
		refreshScoreCard();
		var overrideRollButton = false;
		if (data['current_rolled_dice']['rolledValues'].length > 0 && !isAllNull(data['current_rolled_dice']['rolledValues'])) {
			buildAlreadyRolledDice(data['current_rolled_dice']['rolledValues'], true)
			var overrideRollButton = false;
		}
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
							initiateTurn(overrideRollButton);
							currentPlayerTriggered = true;
							overrideRollButton = false;
						}
					} else {
						currentPlayerTriggered = false;	
						toggleCurrentTurnToolsOff();	
						buildAlreadyRolledDice(data['current_rolled_dice']['rolledValues'], false);
						setCurrentRollScoreSets(data['current_rolled_dice']['scoresets'], false);
					}
				}
			});

		}, 1000)
	}
});
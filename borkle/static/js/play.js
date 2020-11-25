$(document).ready(function playGame(){
	// Just turn off the refresh is the game is over
	var data = checkGameData(false);
	var currentPlayerTriggered = false;
	
	var stillWaiting = true;
	if ( data['game_status'] == 'over' ) {
		var stillWaiting = false;
		var autorefresh = false;
		displayWinner(data['winners']);
		toggleDiceBoard('off');
		refreshScoreCard();
	} else if ( data['game_status'] == 'waiting' ) {
		var autorefresh = true;
		refreshScoreBoard();
		toggleDiceBoard('off');
		toggleScoreCards('off');
	} else {
		var autorefresh = true;
		var stillWaiting = false;
		var practiceGame = data['practice_game'];
		bindRollDice();
		bindScoreDice();
		bindEndTurn(practiceGame);
		refreshScoreCard();
		toggleCurrentTurnToolsOff();
		var overrideRollButton = false;
		if (data['current_rolled_dice']['rolledValues'].length > 0 && !isAllNull(data['current_rolled_dice']['rolledValues'])) {
			buildAlreadyRolledDice(data['current_rolled_dice']['rolledValues'], true);
			setCurrentRollScoreSets(data['current_rolled_dice']['scoresets'], true);
			var overrideRollButton = false;
			var currentPlayerTriggered = true;
			toggleEndTurnButton('on');
			if (data['current_rolled_dice']['scoresets'].length > 0) {
				toggleRollDiceButton('on');
			}
		}
	}
	getPlayerCardData();
	bindScoreCardNav();
	// Set game play functions to refresh
	if (autorefresh) {
		var gameLoop = window.setInterval(function startGameLoop(){

			var needsInitiateTurn = false;
			var refreshGameInfoUrl = $('input#api-gameinfo-url').val();
			var resultData = {};
			$.ajax({
				method: 'GET',
				url: refreshGameInfoUrl,
				dataType: 'json',
				success: function setData(data) {
					resultData = data;	
					if ( data['game_status'] == 'over' ) {
						var autorefresh = false;
						endTurn();
						displayWinner(data['winners']);
						clearGameMessage('last-turn');
						clearGameMessage('borkle');
						toggleDiceBoard('off');
						clearInterval(gameLoop);
					} else if (data['game_status'] == 'active') {
						if ( stillWaiting == true ) {
							refreshScoreBoard();
							toggleDiceBoard('on');
							stillWaiting = false;
							bindRollDice();
							bindScoreDice();
							bindEndTurn(false);
							refreshScoreCard();
							toggleCurrentTurnToolsOff();		
						}
						toggleScoreCards('on');
						var isCurrentPlayer = data['is_current_player'];
						
						if (isCurrentPlayer) {
							if (!currentPlayerTriggered) {
								refreshScoreBoard();
								initiateTurn(overrideRollButton);
								currentPlayerTriggered = true;
								overrideRollButton = false;
							}
							if (data['last_turn']) {
								toggleLastTurn('on');
							}
						} else {
							currentPlayerTriggered = false;	
							toggleOpponentTurn('on', data['current_player']);
							buildAlreadyRolledDice(data['current_rolled_dice']['rolledValues'], false);
							setCurrentRollScoreSets(data['current_rolled_dice']['scoresets'], false);
						}
					}
				}
			});

		}, 1000)
	}
});
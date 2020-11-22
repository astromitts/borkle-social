

function updateAvailableDice(count) {
	var currentAvailableDice = $('span#available-dice-value');
	if (currentAvailableDice.html() != count ) {
		currentAvailableDice.html(count);
	}
}

function updateCurrentScore(count) {
	var currentAvailableDice = $('span#current-score-value');
	if ( currentAvailableDice.html() != count || currentAvailableDice.html() == "" ) {
		currentAvailableDice.html(count);
	}
}

function clearRolledDice(targetDivPrefix){
	rolledDiceFieldNames.forEach(function (rolledDiceId, index) {
		$('div#' + targetDivPrefix + rolledDiceId).html('');
	});
}

function countRolledDice(targetDivPrefix){
	var rolledDiceCount = 0
	rolledDiceFieldNames.forEach(function (rolledDiceId, index) {
		rolledDiceCount += $('img#' + targetDivPrefix + rolledDiceId).length;
	});
	return rolledDiceCount;
}

function bindEndTurn() {
	var endTurnUrl = $('input#api-endturn-url').val();
	$('button#advanceplater').click(function(){
		$.ajax({
			method: 'POST',
			url: endTurnUrl,
			dataType: 'json',
			data: {},
			success: function (data) {
				if (data['status'] == 'error' ) {
					alert(data['message']);
				} else {
					clearRolledDice('slot-');
					$('div#scored-sets').html('');
					toggleRollDiceButton('off');
					toggleSelectedDiceSlot('off');
					toggleBorkleMessage('off');
					toggleAvailableDice('off');
					toggleCurrentScore('off');
					toggleEndTurnButton('off');
				}
			}
		});
	});
}


function clearOpponentBoard() {
	clearRolledDice('opponent-')
	$('div#opponent-selected-dice').html('');
	$('div#opponent-current-score').html('');
	$('div#opponent-available-dice').html('');
	$('div#opponent-scored-sets').html('');
	$('div#opponent-last-turn').html('');
	toggleElementVisibility($('div#opponent-scored-sets'), 'off');
}

function refreshScoreboard() {
	var refreshScoreboardUrl = $('input#api-scoreboard-url').val();
	$.ajax({
		method: 'GET',
		url: refreshScoreboardUrl,
		dataType: 'json',
		success: function (data) {
			$('tr.player-score').each(function(){
				var playerName = $(this).attr('data-player-name');
				if( !data['player_names'].includes(playerName) ) {
					var playerRow = $('tr#scoreboard-player_' + playerName);
					playerRow.html('<td colspan="100%">'+playerName+' left the game</td>');
					playerRow.addClass('player-left-game');
				}
			});

			data['scoreboard'].forEach(function(player){
				var playerName = player['username'];
				var playerScore = player['score'];
				var playerIsCurrent = player['current_player'];
				$('td#scoreboard-player-score_' + playerName).html(playerScore);
				var playerRow = $('tr#scoreboard-player_' + playerName);
				if( playerIsCurrent == true ){
					playerRow.addClass('scoreboard_currentplayer');
				} else {
					playerRow.removeClass('scoreboard_currentplayer');
				}
			});
		}
	});
}

function refreshOpponentBoard() {
	var refreshDiceBoardUrl = $('input#api-diceboard-url').val();
	$.ajax({
		method: 'GET',
		url: refreshDiceBoardUrl,
		dataType: 'json',
		success: function (data) {
			var targetRolledDiceDiv = $('div#opponent-rolled-dice');
			var targetSelectedDiceDiv = $('div#opponent-scored-sets');
			if (data['is_current_player'] == false) {
				if ( data['last_turn'] ){
					$('div#opponent-last-turn').html("<b>It's "+data['current_player']+"'s last turn!!");
				}
				$('div#opponent-current-score').html('<b>'+data['current_player']+'\'s score for this turn: ' + data['current_score'] + '</b>');
				$('div#opponent-available-dice').html('<b>'+data['current_player']+' has ' + data['available_dice_count'] + ' dice left.</b>');
				//setRolledDice(data, 'opponent-', false);
				setCurrentRollScoreSets(data['scoresets'], targetSelectedDiceDiv, false);
			}
		}
	});
}

function displayWinner(winnerData) {
	var winnerDiv = $('div#winner-data');
	if( winnerDiv.length > 0 ){
		if( winnerData['winner_count'] == 1) {
			var winnerHtml = 'The winner is ' + winnerData['winners'][0]['username'] + '! ' + winnerData['winners'][0]['score'] + ' points to '+winnerData['winners'][0]['username'] +'!'
			winnerDiv.html(winnerHtml);
		} else {
			var winnerHtml = "It's a tie!! The winners are: "
			winnerData['winners'].forEach(function(winner){
				winnerHtml = winnerHtml + '<br />'+ winner['username'] + '! ' + winner['score'] + ' points to '+ winner['username'] +'!'
			});
		}
	}
	toggleElementVisibility(winnerDiv, 'on');
}


function setGameMessage(messageText, selector) {
	var gameMessageRow = $('div#row-'+selector+'-message');
	var gameMessageDiv = $('div#'+selector+'-message');
	if (gameMessageDiv.html() != messageText ){
		gameMessageDiv.html(messageText);
	}
	toggleElementVisibility(gameMessageDiv, 'on');
	toggleElementVisibility(gameMessageRow, 'on');
	return 'on';
}

function clearGameMessage(selectId) {
	var gameMessageRow = $('div#row-'+selectId+'-message');
	var gameMessageDiv = $('div#'+selectId+'-message');
	$('div#'+selectId+'-message').html('');
	toggleElementVisibility(gameMessageDiv, 'off');
	toggleElementVisibility(gameMessageRow, 'off');
	return 'off';
}


function hasSelectedDice() {
	return $('img.selected').length > 0;
}

function refreshGameTools(bypass_has_rolled) {
	var gameData = checkGameData();
	var refreshGameInfoUrl = $('input#api-gameinfo-url').val();
	// If the game ended, turn off all the game play tools and display the winner
	if(gameData['game_over']) {
		toggleRollDiceButton('off');
		toggleDiceBoard('off');
		clearOpponentBoard();
		toggleBorkleMessage('off');
		displayWinner(gameData['winners']);
		toggleLastTurn('off');
	} else {
		// If it's my turn, turn on game play tools
		if (gameData['is_current_player'] == true) {
			updateAvailableDice(gameData['available_dice_count']);
			toggleAvailableDice('on');
			updateCurrentScore(gameData['current_rolled_dice']['current_score']);
			toggleCurrentScore('on');
			toggleOpponentScoreSet('off');
			if (gameData['can_roll'] &&! hasSelectedDice()) {
				toggleRollDiceButton('on');
			} else {
				toggleRollDiceButton('off');
			}
			if(gameData['can_end_turn'] && !hasSelectedDice()) {
				toggleEndTurnButton('on');
			} else {
				toggleEndTurnButton('off');
			}
			if(gameData['has_rolled']) {
				toggleDiceBoard('on');
			}
			clearOpponentBoard();
			if (!gameData['borkled']) {
				toggleBorkleMessage('off');
			} else {
				toggleBorkleMessage('on');
			}
		} else {
			toggleOpponentScoreSet('on');
			toggleAvailableDice('off');
			updateAvailableDice(6);
			toggleCurrentScore('off');
			updateCurrentScore(0);
		}
		// If it's my last turn, let me know
		if (gameData['is_current_player'] == true && gameData['last_turn'] == true ) {
			toggleLastTurn('on');
		}
		// If it's not my turn, turn off the last turn game message
		if ( gameData['is_current_player'] == false ){
			toggleLastTurn('off');
		}
	}
}

function checkGameData(isAsync) {
	// Call the gameinfo API and return the data
	var refreshGameInfoUrl = $('input#api-gameinfo-url').val();
	var resultData = {};
	$.ajax({
		method: 'GET',
		url: refreshGameInfoUrl,
		dataType: 'json',
		async: isAsync,
		success: function setData(data) {
			resultData = data;
		}
	});
	return resultData;
}
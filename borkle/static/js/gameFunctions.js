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
					toggleEndTurnButton('off');
					toggleAvailableDice('off');
					toggleCurrentScore('off');
					clearGameMessage();
					refreshScoreboard();
					updateTurnScore(0);
				}
			}
		});
	});
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



function refreshScoreCard() {
	var refreshScoreCardUrl = $('input#api-scorecard-url').val();
	var latestScoreCardInput = document.getElementById('latest-scorecard-turn');
	var latestScoreCardTurn = latestScoreCardInput.value;
	$.ajax({
		method: 'GET',
		url: refreshScoreCardUrl + '?latest_turn=' + latestScoreCardTurn,
		dataType: 'json',
		success: function (data) {
			data['players'].forEach(function(player){
				var playerPK = player['pk'];
				var playerName = player['username'];
				var playerTable = document.getElementById('scorecard_' + playerName);
				player['turns'].forEach(function(turn){
					if( turn['scoresets'].length > 0 ) {
						if ( latestScoreCardTurn < turn['turn_index'] ) {
							latestScoreCardTurn = turn['turn_index'];
						}
						var rowId = 'scorecard-set_' + playerName + '_' + turn['turn_index'];
						scoreCardRowExists = $('tr#' + rowId);
						if (scoreCardRowExists.length == 0) {
							var scoreCardRow = document.createElement('tr');
							scoreCardRow.setAttribute('id', rowId);
							playerTable.prepend(scoreCardRow);

							var turnScoreTD = document.createElement('td');
							turnScoreTD.innerHTML = 'Turn: ' + turn['turn_index'] + '<br />Total: ' + turn['score'];
							scoreCardRow.append(turnScoreTD);

							var scoreSetTD = document.createElement('td');
							turn['scoresets'].forEach(function(scoreset){
								var scoreSetDiv = document.createElement('div');
								scoreset['scoreable_value_images'].forEach(function(value){
									var diceImage = getImageFromCache('scored-dice-cache_' + value);
									scoreSetDiv.append(diceImage);
								});
								var scoreSpan = document.createElement('span'); 
								scoreSpan.innerHTML = '=' + scoreset['score'];
								scoreSetDiv.append(scoreSpan);
								scoreSetTD.append(scoreSetDiv);
							});
							scoreCardRow.append(scoreSetTD);
						}
					}
				});
			});
		}
	});
	latestScoreCardInput.setAttribute('value', latestScoreCardTurn);
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
			toggleAvailableDice('on');
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
			toggleCurrentScore('off');
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

function initiateTurn() {
	updateDiceCount(6);
	toggleAvailableDice('on');
	toggleCurrentScore('on');
	toggleAvailableDice('on');
	toggleCurrentScore('on');
	toggleRollDiceButton('on');
}


function setCurrentRollScoreSets(scoreSets, allowUndo) {
	for (var key of Object.keys(scoreSets)) {
		buildScoreSetTable(scoreSets[key], scoreSets[key]['scorableFields'], true);
	}
}

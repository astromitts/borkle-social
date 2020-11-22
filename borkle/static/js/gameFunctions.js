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

function endTurn() {
	clearRolledDice('slot-');
	$('div#scored-sets').html('');
	toggleCurrentTurnToolsOff();
	clearGameMessage();
	refreshScoreboard();
	updateTurnScore(0);
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
					endTurn();
				}
			}
		});
	});
}

function displayWinner(winnerData) {
	var winnerDiv = $('div#winner-data');
	toggleDiceBoard('off');
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
								if( scoreset['scoreValue'] == 0 ) {
									var diceImage = getImageFromCache('scored-dice-cache_0');
									scoreSetDiv.append(diceImage);
								} else {
									scoreset['scorableValues'].forEach(function(value){
										var diceImage = getImageFromCache('scored-dice-cache_' + value);
										scoreSetDiv.append(diceImage);
									});
								}
								var scoreSpan = document.createElement('span'); 
								scoreSpan.innerHTML = '=' + scoreset['scoreValue'];
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

function initiateTurn(overrideRollButton) {
	clearScoreSetTable();
	updateDiceCount(6);
	toggleAvailableDice('on');
	toggleCurrentScore('on');
	toggleAvailableDice('on');
	toggleCurrentScore('on');
	if (!overrideRollButton) {
		clearRolledDice('slot-');
		toggleRollDiceButton('on');
	}
	refreshScoreCard();
}

function buildAlreadyRolledDice(rolledValues, allowUndo) {
	if (rolledValues.length > 0 && !isAllNull(rolledValues)) {
		var rolledDice = stripNulls(rolledValues);
		var rollHasScore = hasScore(rolledDice);
		setRolledDice(rolledDice, allowUndo, rollHasScore);
	}
}

function setCurrentRollScoreSets(scoreSets, allowUndo) {
	for (var key of Object.keys(scoreSets)) {
		buildScoreSetTable(scoreSets[key], scoreSets[key]['scorableFields'], allowUndo, scoreSets[key]['scoreSetPk']);
	}
}

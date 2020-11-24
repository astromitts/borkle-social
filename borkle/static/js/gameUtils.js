const rolledDiceFieldNames = [
	'rolled_dice_1_value',
	'rolled_dice_2_value',
	'rolled_dice_3_value',
	'rolled_dice_4_value',
	'rolled_dice_5_value',
	'rolled_dice_6_value',
]

function doAsyncPost(targetUrl, postData) {
	$.ajax({
		method: 'POST',
		url: targetUrl,
		dataType: 'json',
		data: postData,
	});
}

function doNonAsyncGet(targetUrl) {
	var resultData;
	$.ajax({
		method: 'GET',
		url: targetUrl,
		dataType: 'json',
		async: false,
		success: function successFunction(data) {
			resultData = data;
		}
	});
	return resultData;
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

function getImageFromCache(imageId) {
	var imgSource = document.getElementById(imageId);
	var imgClone = imgSource.cloneNode();
	return imgClone;
}

function addDice(addAmount) {
	var diceButton = $('button#rolldice');
	var diceAmount = parseInt(diceButton.attr('data-dice-count'));
	var diceAmount = diceAmount + addAmount;
	updateDiceCount(diceAmount);
}

function subtractDice(subtractAmount) {
	var diceButton = $('button#rolldice');
	var diceAmount = parseInt(diceButton.attr('data-dice-count'));
	var diceAmount = diceAmount - subtractAmount;
	if ( diceAmount === 0 ) {
		diceAmount = 6;
	}
	updateDiceCount(diceAmount);
}

function updateDiceCount(diceAmount) {
	var diceButton = $('button#rolldice');
	diceButton.attr('data-dice-count', diceAmount);
	var currentAvailableDice = $('span#available-dice-value');
	if (currentAvailableDice.html() != diceAmount ) {
		currentAvailableDice.html(diceAmount);
	}
}

function updateTurnScore(scoreIncrease) {
	var currentScoreSpan = $('span#current-score-value');
	if (scoreIncrease == 0) {
		var newScore = 0;
	} else {
		var currentScoreValue = parseInt(currentScoreSpan.html());
		var newScore = currentScoreValue + scoreIncrease;
	}
	currentScoreSpan.html(newScore);
	return newScore;
}

function decreaseTurnScore(scoreDecrease) {
	var currentScoreSpan = $('span#current-score-value');
	var currentScoreValue = parseInt(currentScoreSpan.html());
	var newScore = currentScoreValue - scoreDecrease;
	if (newScore == 0) {
		newScore = "0";
	}
	currentScoreSpan.html(newScore);
	return newScore;
}

function clearRolledDice(targetDivPrefix){
	$('table#dice-table').removeClass('dice-table_active');
	rolledDiceFieldNames.forEach(function (rolledDiceId, index) {
		$('td#' + targetDivPrefix + rolledDiceId).html('');
	});
}

function clearUndoButtons() {
	$('button.undo-score-selection').each(function clearUndoButton(){
		$(this).remove();
	});
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

function endTurn() {
	clearRolledDice('slot-');
	$('div#scored-sets').html('');
	toggleCurrentTurnToolsOff();
	clearGameMessage();
	refreshScoreboard();
	updateTurnScore(0);
}

function bindEndTurn(practiceGame) {
	var endTurnUrl = $('input#api-endturn-url').val();
	$('button#advanceplater').click(function endTurnClicked(){
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
					if( practiceGame ) {
						initiateTurn();
					}
				}
			}
		});
	});
}

function displayWinner(winnerData) {
	var winnerDiv = $('div#winner-data');
	toggleDiceBoard('off');
	if( winnerData['winner_count'] == 1) {
		var winnerHtml = 'The winner is ' + winnerData['winners'][0]['username'] + '! ' + winnerData['winners'][0]['score'] + ' points to '+winnerData['winners'][0]['username'] +'!';
	} else {
		var winnerHtml = "It's a tie!! The winners are: "
		winnerData['winners'].forEach(function addWinners(winner){
			winnerHtml = winnerHtml + '<br />'+ winner['username'] + '! ' + winner['score'] + ' points to '+ winner['username'] +'!';
		});
	}
	if (winnerDiv.html() != winnerHtml) {
		winnerDiv.html(winnerHtml);
	}
	var winnerRow = $('.winner-data');
	toggleElementVisibility(winnerRow, 'on');
}


function refreshScoreboard() {
	var refreshScoreboardUrl = $('input#api-scoreboard-url').val();
	$.ajax({
		method: 'GET',
		url: refreshScoreboardUrl,
		dataType: 'json',
		success: function (data) {
			$('tr.player-score').each(function checkIfPlayerLeft(){
				var playerName = $(this).attr('data-player-name');
				if( !data['player_names'].includes(playerName) ) {
					var playerRow = $('tr#scoreboard-player_' + playerName);
					playerRow.html('<td colspan="100%">'+playerName+' left the game</td>');
					playerRow.addClass('player-left-game');
				}
			});

			data['scoreboard'].forEach(function updatePlayerScore(player){
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
			data['players'].forEach(function refreshPlayerScoreCard(player){
				var playerPK = player['pk'];
				var playerName = player['username'];
				var playerTable = document.getElementById('tbody-scorecard_' + playerName);
				player['turns'].forEach(function updateTurn(turn){
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
							turn['scoresets'].forEach(function addScoreset(scoreset){
								var scoreSetDiv = document.createElement('div');
								if( scoreset.scoreValue == 0 ) {
									var diceImage = getImageFromCache('scored-dice-cache_0');
									scoreSetDiv.append(diceImage);
								} else {
									scoreset.scorableValues.forEach(function addScoreableImages(value){
										var diceImage = getImageFromCache('scored-dice-cache_' + value);
										scoreSetDiv.append(diceImage);
									});
								}
								var scoreSpan = document.createElement('span'); 
								scoreSpan.innerHTML = '=' + scoreset.scoreValue;
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
	toggleSelectedDiceSlot('off');
	toggleAvailableDice('on');
	toggleCurrentScore('on');
	toggleAvailableDice('on');
	toggleCurrentScore('on');
	toggleOpponentTurn('off');
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


function clearScoreSetTable(visibility) {
	$('div#scored-sets').html('');
}

function isAllNull(testList) {
	var nullCount = 0;
	testList.forEach(function checkIfNull(val){
		if(val == null){
			nullCount++;
		}
	});
	return nullCount == testList.length;
}

function stripNulls(diceSet) {
	var nonNulls = [];
	diceSet.forEach(function removeNull(val) {
		if(val == null == false){
			nonNulls.push(val);
		}
	});
	return nonNulls;
}

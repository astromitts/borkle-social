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

function clearRolledDice(targetDivPrefix){
	rolledDiceFieldNames.forEach(function (rolledDiceId, index) {
		$('div#' + targetDivPrefix + rolledDiceId).html('');
	});
}

function clearUndoButtons() {
	$('button.undo-score-selection').each(function(){
		$(this).remove();
	});
}

function buildScoreSetTable(selectedDiceScore, sourceIds, allowUndo, scoreSetPk) {
	var targetSelectedDiceDiv = $('div#selected-dice');
	var targetScoredDiveDiv = $('div#scored-sets');
	var scoreTableExists = $("table#scoreset_table").length > 0;
	if (!scoreTableExists ) {
		var scoreTable = document.createElement("table");
		scoreTable.setAttribute('id', 'scoreset_table');
		if (allowUndo) {
			targetScoredDiveDiv.append(document.createElement('hr'));
		}
		var header = document.createElement('h5');
		header.innerHTML = 'Scored Sets';
		targetScoredDiveDiv.append(header);
		targetScoredDiveDiv.append(scoreTable);
	} else {
		var scoreTable = document.getElementById('scoreset_table')
	}
	if ( scoreSetPk ) {
		var scoreRowExists = $('tr#scoreset_row_' + scoreSetPk).length > 0;
		if ( scoreRowExists ) {
			var scoreRow = document.getElementById('scoreset_row_' + scoreSetPk);
			var needsBuild = false;
		} else {
			var scoreRow = document.createElement('tr');
			scoreRow.setAttribute('id', 'scoreset_row_' + scoreSetPk);
			var needsBuild = true;
		}
	} else {
		var scoreRow = document.createElement('tr');
		var needsBuild = true;
	}
	if ( needsBuild ) {
		var diceImgCell = document.createElement('td');
		if ( allowUndo && selectedDiceScore['locked'] == false) {
			var undoSpan = document.createElement('span');
			undoSpan.setAttribute('class', 'span-undo-btn');
			var undoButton = document.createElement('button');
			undoButton.innerHTML = 'undo';
			undoButton.setAttribute('class', 'game-btn undo-score-selection');
			undoSpan.append(undoButton);
			diceImgCell.append(undoSpan);
			bindUndoScoreSetSelection(undoButton);
		} else if (allowUndo) {
			var undoSpan = document.createElement('span');
			undoSpan.setAttribute('class', 'span-undo-btn');
			diceImgCell.append(undoSpan);
		}
		var scoreText = document.createTextNode(selectedDiceScore['scoreValue'] + ' = ');
		diceImgCell.append(scoreText);
		for (var key of Object.keys(selectedDiceScore['scorableValues'])) {
			var diceValue = selectedDiceScore['scorableValues'][key];
			var diceImage = getImageFromCache('scored-dice-cache_' + diceValue);
			diceImage.setAttribute('data-source-slot', sourceIds[key]);
			diceImgCell.append(diceImage);
		}
		scoreRow.append(diceImgCell);
		scoreTable.prepend(scoreRow);
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


function clearScoreSetTable(visibility) {
	$('div#scored-sets').html('');
}

function isAllNull(testList) {
	var nullCount = 0;
	testList.forEach(function(val){
		if(val == null){
			nullCount++;
		}
	});
	return nullCount == testList.length;
}

function stripNulls(diceSet) {
	var nonNulls = [];
	diceSet.forEach(function(val) {
		if(val == null == false){
			nonNulls.push(val);
		}
	});
	return nonNulls;
}

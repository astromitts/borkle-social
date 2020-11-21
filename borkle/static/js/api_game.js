const rolledDiceFieldNames = [
	'rolled_dice_1_value',
	'rolled_dice_2_value',
	'rolled_dice_3_value',
	'rolled_dice_4_value',
	'rolled_dice_5_value',
	'rolled_dice_6_value',
]

function getImageFromCache(imageId) {
	var imgSource = document.getElementById(imageId);
	var imgClone = imgSource.cloneNode();
	return imgClone;
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

function bindUndoScoreSetSelection() {
	var undoSelectionUrl = $('input#api-undoselection-url').val();
	$('button.undo-score-selection').click(function(){
		var scoreSetID = $(this).attr('id');
		$.ajax({
			method: 'POST',
			url: undoSelectionUrl,
			dataType: 'json',
			data: {'scoreset_pk': scoreSetID},
			success: function (data) {
				if (data['status'] == 'error' ) {
					alert(data['message']);
				} else {
					clearRolledDice();
					$('tr#scoreset_' + scoreSetID).remove()
					setRolledDice(data['current_rolled_dice'], 'slot-');
					bindSelectDice();
				}
			}
		});
	});
}

function setCurrentRollScoreSets(scoreSets, targetDiv, allowUndo) {
	var scoreTableExists = $("table#scoreset_table");
	if (scoreTableExists.length == 0 ) {
		var header = document.createElement('h4');
		header.innerHTML = 'Scored Sets';
		targetDiv.append(header);
		var scoreTable = document.createElement("table");
		scoreTable.setAttribute('id', 'scoreset_table');
	} else {
		var scoreTable = document.getElementById('scoreset_table')
	}
	scoreSets.forEach(function (scoreSet, index) {
		row_exists = $('tr#' + 'scoreset_' + scoreSet['pk']).length
		if( row_exists == 0 ){
			var scoreRow = document.createElement("tr");
			scoreRow.setAttribute('id', 'scoreset_' + scoreSet['pk']);
			var diceImgCell = document.createElement("td");
			scoreSet['scoreable_value_images'].forEach(function (imageValue, index) {
				diceImage = getImageFromCache('scored-dice-cache_' + imageValue);
				diceImgCell.append(diceImage);
			});
			var diceScoreCell = document.createElement("td");
			diceScoreCell.innerHTML = "= " + scoreSet['score'];
			
			var toolCell = document.createElement("td");
			if (scoreSet['locked'] == false && allowUndo) {
				var undoBtn = document.createElement("button");
				undoBtn['innerHTML'] = 'Undo';
				undoBtn.setAttribute('id', scoreSet['pk']);
				undoBtn.setAttribute('class', 'game-btn undo-score-selection');
				toolCell.append(undoBtn);
			}

			scoreRow.append(diceImgCell);
			scoreRow.append(diceScoreCell);
			scoreRow.append(toolCell);
			scoreTable.prepend(scoreRow);
		}
	});
	targetDiv.append(scoreTable);
	bindUndoScoreSetSelection();
}

function bindScoreDice() {
	var scoreDiceUrl = $('input#api-scoredice-url').val();
	$('button#score-selected-dice').click(function(){
		selectedDiceIds = {};
		$('img.selected').each(function(){
			selectedDiceIds[$(this).attr('id')] = 'select';
		});
		$.ajax({
			method: 'POST',
			url: scoreDiceUrl,
			dataType: 'json',
			data: selectedDiceIds,
			success: function (data) {
				if (data['status'] == 'error' ) {
					alert(data['message']);
				} else {
					var targetSelectedDiceDiv = $('div#selected-dice');
					var targetScoredDiveDiv = $('div#scored-sets');
					$('img.selected').each(function(){
						$(this).remove();
					});
					setCurrentRollScoreSets(data['scoresets'], targetScoredDiveDiv, true);
					toggleEndTurnButton('on');
					toggleDiceButton('on');
					toggleSelectedDiceSlot('off');
				}
			}
		});
	});
}

function bindSelectDice() {
	$('img.rolled-dice_selectable').click(function(){
		var diceId = $(this).attr('id');
		var diceElement = document.getElementById(diceId);
		if ( diceElement.parentNode.id == 'selected-dice-slot') {
			document.getElementById('slot-' + diceId).appendChild(diceElement);
			$(this).removeClass('selected');
		} else {
			$(this).addClass('selected');
			var colDiv = document.createElement('div');
			var selectedDiceRow = document.getElementById('selected-dice-slot');
			colDiv.setAttribute('class', 'col');
			colDiv.setAttribute('id', 'selected-dice_' + diceId);
			
			colDiv.appendChild(diceElement);

			selectedDiceRow.appendChild(diceElement); 
		}
		if ($('img.selected').length > 0) {
			toggleSelectedDiceSlot('on');
			toggleEndTurnButton('off');
			toggleDiceButton('off');
		} else {
			toggleSelectedDiceSlot('off');
			toggleEndTurnButton('on');
		}
	});
}

function clearUndoButtons() {
	$('button.undo-score-selection').each(function(){
		$(this).remove();
	});
}

function clearRolledDice(targetDivPrefix){
	rolledDiceFieldNames.forEach(function (rolledDiceId, index) {
		$('div#' + targetDivPrefix + rolledDiceId).html('');
	});}

function countRolledDice(targetDivPrefix){
	var rolledDiceCount = 0
	rolledDiceFieldNames.forEach(function (rolledDiceId, index) {
		rolledDiceCount += $('img#' + targetDivPrefix + rolledDiceId).length;
	});
	return rolledDiceCount;
}

function bindRollDice() {
	var rollDiceUrl = $('input#api-rolldice-url').val();
	var targetDivPrefix =  'slot-';
	
	$('button#rolldice').click(function(){
		clearRolledDice(targetDivPrefix);
		toggleBorkleMessage('off');
		toggleDiceButton('off');
		$.ajax({
			method: 'POST',
			url: rollDiceUrl,
			dataType: 'json',
			data: {},
			success: function (data) {
				if (data['status'] == 'error' ) {
					alert(data['message']);
				} else {
					clearUndoButtons();
					setRolledDice(data, 'slot-');
					toggleSelectedDiceSlot('off');
					if ( data['available_score'] ) {
						bindSelectDice();
					} else {
						toggleBorkleMessage('on');
						toggleEndTurnButton('on');
					}
				}
			}
		});
	});
}

function setRolledDice(data, targetDivPrefix){
	rolledDiceFieldNames.forEach(function (rolledDiceId, index) {
		var needs_refresh;
		var value = data[rolledDiceId]['value'];
		if (value != null) {
			var dice_already_exists = $('img#' + rolledDiceId);
			if (dice_already_exists.length > 0) {
				var current_image = dice_already_exists.attr('src');
				needs_refresh = current_image != data[rolledDiceId]['image'];
			} else {
				needs_refresh = true;
			}
			if ( needs_refresh ) {
				var targetDiv = document.getElementById(targetDivPrefix + rolledDiceId);
				$('img#' + rolledDiceId).remove();
				if (data['is_current_player'] == true && data['available_score']) {
					diceClass = 'rolled-dice rolled-dice_selectable';
				} else {
					diceClass = 'rolled-dice';
				}
				var cacheImageId = 'rolled-dice-cache_' + value;
				var diceImage = getImageFromCache(cacheImageId)
				diceImage.setAttribute('class', diceClass);
				diceImage.setAttribute('id', rolledDiceId);
				targetDiv.append(diceImage);
			}
		} else {
			$('img#' + rolledDiceId).remove();
		}
	});
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
					toggleDiceButton('off');
					toggleSelectedDiceSlot('off');
					toggleBorkleMessage('off');
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
				$('div#opponent-available-dice').html('<b>'+data['current_player']+' has ' + data['available_dice'] + ' dice left.</b>');
				setRolledDice(data, 'opponent-');
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

function toggleDiceButton(visibility) {
	var rollDiceButton = $('button#rolldice');
	if (visibility == 'on') {
		toggleElementVisibility(rollDiceButton, 'on');
	} else {
		toggleElementVisibility(rollDiceButton, 'off');
	}
	return visibility;
}

function toggleBorkleMessage(visibility) {
	if( visibility == 'on' ){
		setGameMessage("Oh no you borkled! Your turn is over :( :(", 'borkle');
	} else {
		clearGameMessage('borkle');
	}
	return visibility;
}

function toggleLastTurn(visibility) {
	if( visibility == 'on' ){
		setGameMessage("It's your last turn!!!", 'last-turn');
	} else {
		clearGameMessage('last-turn');
	}
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

function toggleSelectedDiceSlot(visibility) {
	var targetDiv = $('div#selected-dice-slot');
	var targetBtn = $('button#score-selected-dice');
	if (visibility == 'on') {
		toggleElementVisibility(targetDiv, 'on');
		toggleElementVisibility(targetBtn, 'on');
		targetDiv.addClass('selected-dice-slot_active')
	} else {
		toggleElementVisibility(targetDiv, 'off');
		toggleElementVisibility(targetBtn, 'off');
		targetDiv.removeClass('selected-dice-slot_active');
	}
}

function toggleEndTurnButton(visibility) {
	var endTurnButton = $('button#advanceplater');
	if (visibility == 'on') {
		toggleElementVisibility(endTurnButton, 'on')
	} else {
		toggleElementVisibility(endTurnButton, 'off')
	}
	return visibility;
}

function toggleDiceBoard(visibility) {
	var targetRolledDiceDiv = $('div#rolled-dice');
	var targetSelectedDiceDiv = $('div#selected-dice');
	if (visibility == 'on') {
		toggleElementVisibility(targetRolledDiceDiv, 'on');
		toggleElementVisibility(targetSelectedDiceDiv, 'on');
	} else {
		toggleElementVisibility(targetRolledDiceDiv, 'off');
		toggleElementVisibility(targetSelectedDiceDiv, 'off');
	}
}

function toggleElementVisibility(target, visibility) {
	if (visibility == 'on' && target.hasClass('hidden')) {
		target.removeClass('hidden');
	} else if (visibility == 'off' && !target.hasClass('hidden')) {
		target.addClass('hidden');
	}
}

function hasSelectedDice() {
	return $('img.selected').length > 0;
}

function refreshGameTools(bypass_has_rolled) {
	var gameData = checkGameData();
	var refreshGameInfoUrl = $('input#api-gameinfo-url').val();
	// If the game ended, turn off all the game play tools and display the winner
	if(gameData['game_over']) {
		toggleDiceButton('off');
		toggleDiceBoard('off');
		clearOpponentBoard();
		toggleBorkleMessage('off');
		displayWinner(gameData['winners']);
		toggleLastTurn('off');
	} else {
		// If it's my turn, turn on game play tools
		if (gameData['is_current_player'] == true) {
			if (gameData['can_roll'] &&! hasSelectedDice()) {
				toggleDiceButton('on');
			} else {
				toggleDiceButton('off');
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

function checkGameData() {
	// Call the gameinfo API and return the data
	var refreshGameInfoUrl = $('input#api-gameinfo-url').val();
	var resultData = {};
	$.ajax({
		method: 'GET',
		url: refreshGameInfoUrl,
		dataType: 'json',
		async: false,
		success: function setData(data) {
			resultData = data;
		}
	});
	return resultData;
}

$(document).ready(function playGame(){
	// Just turn off the refresh is the game is over
	var data = checkGameData();
	if ( data['game_over'] ) {
		var autorefresh = false;
		displayWinner(data['winners']);
	} else {
		var autorefresh = true;
	}

	// Set up game tools if it's my turn
	if (data['is_current_player']) {
		toggleDiceBoard('on');
		if (data['can_roll']) {
			toggleDiceButton('on');
		} else {
			toggleDiceButton('off');
		}
		if(data['can_end_turn']) {
			toggleEndTurnButton('on');
		} else {
			toggleEndTurnButton('off');
		}
		setRolledDice(data['current_rolled_dice'], 'slot-');
		setCurrentRollScoreSets(data['current_score_sets'], $('div#scored-sets'), true);
	}
	refreshScoreboard();
	bindRollDice();
	bindSelectDice();
	bindScoreDice();
	bindEndTurn();
	refreshScoreCard();
	refreshGameTools();

	// Set game play functions to refresh
	if (autorefresh) {
		window.setInterval(function(){
			refreshGameTools();
			refreshOpponentBoard();
			refreshScoreCard();
			refreshScoreboard();
		}, 1000)
	}
});
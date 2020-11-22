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

function buildScoreSetTable(selectedDiceScore, sourceIds, allowUndo) {
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
	var scoreRow = document.createElement('tr');
	var diceImgCell = document.createElement('td');
	if ( allowUndo && selectedDiceScore['locked'] == false) {
		var undoButton = document.createElement('button');
		undoButton.innerHTML = 'undo';
		undoButton.setAttribute('class', 'game-btn undo-score-selection');
		diceImgCell.append(undoButton);
		bindUndoScoreSetSelection(undoButton);
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
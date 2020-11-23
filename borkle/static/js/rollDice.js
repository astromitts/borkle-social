function bindRollDice() {
	var rollDiceUrl = $('input#api-rolldice-url').val();
	var targetDivPrefix =  'slot-';
	
	$('button#rolldice').click(function(){
		clearRolledDice(targetDivPrefix);
		toggleBorkleMessage('off');
		toggleRollDiceButton('off');

		clearUndoButtons();
		var diceAmount = parseInt($(this).attr('data-dice-count'));
		var rolledDice = rollDice(diceAmount);
		var rollHasScore = hasScore(rolledDice);
		setRolledDice(rolledDice, 'slot-', true, rollHasScore);
		toggleSelectedDiceSlot('off');
		var postData = {}
		if ( !rollHasScore ) {
			toggleBorkleMessage('on');
			toggleEndTurnButton('on');
			toggleAvailableDice('off');
			toggleCurrentScore('off');
			var rollDiceUrl = $('input#api-borkle-url').val();
		} else {
			var rollDiceUrl = $('input#api-rolldice-url').val();
		}
		for (var key of Object.keys(rolledDice)) {
			var slot = parseInt(key);
			postData['rolled_dice_' + slot] = rolledDice[key]
		}
		doAsyncPost(rollDiceUrl, postData)
	});
			
}

function setRolledDice(rolledDice, setSelectable, rollHasScore){
	for (var key of Object.keys(rolledDiceFieldNames)) {
		var diceValue = rolledDice[key];
		var diceSlotId = rolledDiceFieldNames[key];
		var diceCacheID = 'rolled-dice-cache_' + diceValue;
		var existingImageInSlot = $('img#'+diceSlotId);
		if (diceValue != null) {
			var diceImage = getImageFromCache(diceCacheID);
			if (existingImageInSlot.length == 0 || !diceImage['src'].includes(existingImageInSlot.attr('src'))) {
				var needsRefresh = true;
			} else {
				var needsRefresh = false;
			}
			if (needsRefresh == true) {
				if (existingImageInSlot.length > 0) {
					existingImageInSlot.remove();
				}

				var targetDiv = document.getElementById('slot-' + diceSlotId);
				if (setSelectable && rollHasScore) {
					diceClass = 'rolled-dice rolled-dice_selectable';
				} else {
					diceClass = 'rolled-dice';
				}
				diceImage.setAttribute('class', diceClass);
				diceImage.setAttribute('id', diceSlotId);
				targetDiv.append(diceImage);
				bindSelectDice($('img#' + diceSlotId));
			} 
		} else {
			if (existingImageInSlot.length > 0) {
				existingImageInSlot.remove();
			}
		}
	}
}

function hasSelectedDice() {
	return $('img.selected').length > 0;
}

function hasScoredDiceThisTurn() {
	return $('button.undo-score-selection').length > 0;
}

function getSelectedDiceScore() {
	selectedDiceIds = {};
	selectedDiceValues = [];
	$('img.selected').each(function(){
		selectedDiceValues.push($(this).attr('data-value'));
		selectedDiceIds[$(this).attr('id')] = 'select';
	});

	var selectedDiceScore = scoreDiceSet(selectedDiceValues);
	return selectedDiceScore;
}

function bindSelectDice(image) {
	image.click(function(){
		var diceId = $(this).attr('id');
		var diceElement = document.getElementById(diceId);
		if ( diceElement.parentNode.id == 'selected-dice-images') {
			document.getElementById('slot-' + diceId).appendChild(diceElement);
			$(this).removeClass('selected');
		} else {
			$(this).addClass('selected');
			var colDiv = document.createElement('div');
			var selectedDiceRow = document.getElementById('selected-dice-images');
			colDiv.setAttribute('class', 'col');
			colDiv.setAttribute('id', 'selected-dice_' + diceId);
			
			colDiv.appendChild(diceElement);

			selectedDiceRow.appendChild(diceElement); 
		}
		if (hasSelectedDice()) {
			toggleEndTurnButton('off');
			toggleRollDiceButton('off');
			toggleSelectedDiceSlot('on');
			selectedDiceScore = getSelectedDiceScore()
			if (selectedDiceScore.hasScore == true) {
				toggleSelectedDiceButton('on');
				$('#selected-dice-score').html(selectedDiceScore.scoreType + '<br />' + selectedDiceScore.scoreValue + ' Points');
			} else {
				toggleSelectedDiceButton('off');
				$('#selected-dice-score').html('No Score');
			}
		} else {
			toggleSelectedDiceSlot('off');
			toggleSelectedDiceButton('off');
			if (hasScoredDiceThisTurn()) {
				toggleEndTurnButton('on');
			}
		}
	});
}

function bindScoreDice() {
	var scoreDiceUrl = $('input#api-scoredice-url').val();
	$('button#score-selected-dice').click(function(){
		var selectedDiceScore = getSelectedDiceScore();
		if (selectedDiceScore.hasScore) {
			postData = {
				'score': selectedDiceScore.scoreValue,
				'score_type': selectedDiceScore.scoreType,
			}
			$('img.selected').each(function(){
				postData[$(this).attr('id')] = 'score';
			});
			doAsyncPost(scoreDiceUrl, postData);
			scoreSelection(selectedDiceScore, true);
			updateTurnScore(selectedDiceScore.scoreValue);
		} else {
			alert('that is not a score, try something else');
		}
	});
}

function scoreSelection(selectedDiceScore, allowUndo) {
	var sourceIds = [];
	$('img.selected').each(function(){
		sourceIds.push($(this).attr('id'));
		$(this).remove();
	});
	buildScoreSetTable(selectedDiceScore, sourceIds, true);
	toggleSelectedDiceSlot('off');
	toggleSelectedDiceButton('off');
	toggleEndTurnButton('on');
	toggleRollDiceButton('on');
	subtractDice(selectedDiceScore.scorableValues.length);
}

function bindUndoScoreSetSelection(targetButton) {
	var undoSelectionUrl = $('input#api-undoselection-url').val();
	$(targetButton).click(function(){
		var rowToUndo = $(this).closest('tr');
		var addDiceCount = 0;
		rowToUndo.find('img').each(function(){
			var targetSlotId = $(this).attr('data-source-slot');
			var targetSlot = $('div#slot-' + targetSlotId);
			var diceValue = $(this).attr('data-value');
			var diceCacheID = 'rolled-dice-cache_' + diceValue;
			var diceClass = 'rolled-dice rolled-dice_selectable';
			var diceImage = getImageFromCache(diceCacheID);
			diceImage.setAttribute('class', diceClass);
			diceImage.setAttribute('id', targetSlotId);
			targetSlot.append(diceImage);
			bindSelectDice($('img#' + targetSlotId));
			$(this).remove();
			rowToUndo.remove();
			addDiceCount += 1;
			addDice(addDiceCount);
		});
	});
}

function buildScoreSetTable(selectedDiceScore, sourceIds, allowUndo, scoreSetPk) {
	var targetSelectedDiceDiv = $('div#selected-dice');
	var targetScoredDiceDiv = $('div#scored-sets');
	var scoreTableExists = $("table#scoreset_table").length > 0;
	if (!scoreTableExists ) {
		var scoreTable = document.createElement("table");
		scoreTable.setAttribute('id', 'scoreset_table');
		var header = document.createElement('h5');
		header.innerHTML = 'Scored Sets';
		targetScoredDiceDiv.append(header);
		targetScoredDiceDiv.append(scoreTable);
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
		diceImgCell.append(document.createElement('hr'));

		if ( allowUndo && selectedDiceScore.locked == false) {
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

		var scoredImagesSpan = document.createElement('span');
		scoredImagesSpan.setAttribute('class', 'scored-dice-images');

		var scoreTextSpan = document.createElement('span');
		scoreTextSpan.setAttribute('class', 'span-score-value');
		scoreTextSpan.innerHTML = selectedDiceScore.scoreValue + ' = ';
		diceImgCell.append(scoreTextSpan);

		for (var key of Object.keys(selectedDiceScore.scorableValues)) {
			var diceValue = selectedDiceScore.scorableValues[key];
			var diceImage = getImageFromCache('scored-dice-cache_' + diceValue);
			diceImage.setAttribute('data-source-slot', sourceIds[key]);
			scoredImagesSpan.append(diceImage);
		}

		diceImgCell.append(scoredImagesSpan);

		scoreRow.append(diceImgCell);
		scoreTable.prepend(scoreRow);
	}
}
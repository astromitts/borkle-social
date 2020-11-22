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

function setRolledDice(rolledDice, targetDivPrefix, setSelectable, rollHasScore){
	for (var key of Object.keys(rolledDice)) {
		var diceValue = rolledDice[key];
		var diceSlotId = parseInt(key) + 1;
		var diceCacheID = 'rolled-dice-cache_' + diceValue;
		var rolledDiceID = 'rolled_dice_'+diceSlotId+'_value';
		var diceImage = getImageFromCache(diceCacheID);
		var existingImageInSlot = $('img#'+rolledDiceID);
		if (existingImageInSlot.length > 0 && !diceImage['src'].includes(existingImageInSlot.attr('src'))) {
			var needsRefresh = true;
		} else if (diceValue && existingImageInSlot.length == 0) {
			var needsRefresh = true;
		} else {
			var needsRefresh = false;
		}
		if (diceValue != null && needsRefresh) {
			existingImageInSlot.remove();
			var targetDiv = document.getElementById(targetDivPrefix + rolledDiceID);
			if (setSelectable && rollHasScore) {
				diceClass = 'rolled-dice rolled-dice_selectable';
			} else {
				diceClass = 'rolled-dice';
			}
			diceImage.setAttribute('class', diceClass);
			diceImage.setAttribute('id', rolledDiceID);
			targetDiv.append(diceImage);
			bindSelectDice($('img#' + rolledDiceID));
		} 
	}
}

function hasSelectedDice() {
	return $('img.selected').length > 0;
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
			if (selectedDiceScore['hasScore'] == true) {
				toggleSelectedDiceButton('on');
				$('#selected-dice-score').html(selectedDiceScore['scoreValue'] + ' = ');
			} else {
				toggleSelectedDiceButton('off');
				$('#selected-dice-score').html('0 = ');
			}
		} else {
			toggleSelectedDiceSlot('off');
			toggleSelectedDiceButton('off');
			toggleEndTurnButton('on');
		}
	});
}

function bindScoreDice() {
	var scoreDiceUrl = $('input#api-scoredice-url').val();
	$('button#score-selected-dice').click(function(){
		var selectedDiceScore = getSelectedDiceScore();
		if (selectedDiceScore['hasScore']) {
			postData = {
				'score': selectedDiceScore['scoreValue'],
				'score_type': selectedDiceScore['scoreType'],
			}
			$('img.selected').each(function(){
				postData[$(this).attr('id')] = 'score';
			});
			doAsyncPost(scoreDiceUrl, postData);
			scoreSelection(selectedDiceScore, true);
			updateTurnScore(selectedDiceScore['scoreValue']);
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
	subtractDice(selectedDiceScore['scorableValues'].length);
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
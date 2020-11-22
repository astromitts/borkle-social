function toggleRollDiceButton(visibility) {
	var rollDiceButton = $('button#rolldice');
	if (visibility == 'on') {
		toggleElementVisibility(rollDiceButton, 'on');
	} else {
		toggleElementVisibility(rollDiceButton, 'off');
	}
	return visibility;
}

function toggleAvailableDice(visibility) {
	var targetDiv = $('div#available-dice');
	if (visibility == 'on') {
		toggleElementVisibility(targetDiv, 'on');
	} else {
		toggleElementVisibility(targetDiv, 'off');
	}
	return visibility;
}

function toggleCurrentScore(visibility) {
	var targetDiv = $('div#current-score');
	if (visibility == 'on') {
		toggleElementVisibility(targetDiv, 'on');
	} else {
		toggleElementVisibility(targetDiv, 'off');
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

function toggleOpponentTurn(visibility, playername) {
	if( visibility == 'on' ){
		setGameMessage("It's "+playername+"'s' last turn!!!", 'last-turn');
	} else {
		clearGameMessage('last-turn');
	}
}

function toggleSelectedDiceButton(visibility) {
	var targetBtn = $('div#score-dice-btn-row');
	if (visibility == 'on') {
		toggleElementVisibility(targetBtn, 'on');
	} else {
		toggleElementVisibility(targetBtn, 'off');
	}
	return visibility;
}

function toggleSelectedDiceSlot(visibility) {
	var targetDiv = $('div#selected-dice-slot');
	if (visibility == 'on') {
		toggleElementVisibility(targetDiv, 'on');
		targetDiv.addClass('selected-dice-slot_active')
	} else {
		toggleElementVisibility(targetDiv, 'off');
		targetDiv.removeClass('selected-dice-slot_active');
	}
	return visibility;
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

function toggleCurrentTurnToolsOff() {
	toggleRollDiceButton('off');
	toggleSelectedDiceSlot('off');
	toggleBorkleMessage('off');
	toggleEndTurnButton('off');
	toggleAvailableDice('off');
	toggleCurrentScore('off');
}


function toggleOpponentScoreSet(visibility) {
	var targetDiv = $('div#opponent-scored-sets');
	if ( visibility == 'on' ){
		toggleElementVisibility(targetDiv, 'on');
	} else {
		toggleElementVisibility(targetDiv, 'off');
	}
	return visibility;
}

function toggleElementVisibility(target, visibility) {
	if (visibility == 'on' && target.hasClass('hidden')) {
		target.removeClass('hidden');
	} else if (visibility == 'off' && !target.hasClass('hidden')) {
		target.addClass('hidden');
	}
}

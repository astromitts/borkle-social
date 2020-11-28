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

function toggleOpponentTurn(visibility, currentPlayer) {
	var messageText;
	if( visibility == 'on' ){
		toggleCurrentScore('off');
		if ( currentPlayer.last_turn ) {
			messageText = "It's "+currentPlayer.player_name+"'s last turn!!!";
		} else {
			messageText = "It's "+currentPlayer.player_name+"'s turn!";
		}
		setGameMessage(messageText, 'last-turn');
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
	var playBoard = $('div#play-board');
	if (visibility == 'on') {
		toggleElementVisibility(playBoard, 'on');
	} else {
		toggleElementVisibility(playBoard, 'off');
	}
	return visibility;
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

function toggleScoreCards(visibility) {
		var targetDiv = $('.scorecard-toggle');
	if ( visibility == 'on' ){
		toggleElementVisibility(targetDiv, 'on');
	} else {
		toggleElementVisibility(targetDiv, 'off');
	}
	return visibility;
}

function setGameMessage(messageText, selector) {
	var gameMessageRow = $('div#'+selector+'-message');
	var gameMessageDiv = $('div#'+selector+'-message');
	if (gameMessageDiv.html() != messageText ){
		gameMessageDiv.html(messageText);
	}
	toggleElementVisibility(gameMessageDiv, 'on');
	toggleElementVisibility(gameMessageRow, 'on');
	return 'on';
}

function clearGameMessage(selectId) {
	var gameMessageRow = $('div#'+selectId+'-message');
	var gameMessageDiv = $('div#'+selectId+'-message');
	$('div#'+selectId+'-message').html('');
	toggleElementVisibility(gameMessageDiv, 'off');
	toggleElementVisibility(gameMessageRow, 'off');
	return 'off';
}

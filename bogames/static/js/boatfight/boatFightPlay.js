function togglePlayerBoard(visibility) {
	return visibility;
}

function toggleOpponentBoard(visibility) {
	var playerTools = $('#current-turn-tools');
	toggleElementVisibility(playerTools, visibility);
	return visibility;
}

function toggleWinner(winner) {
	var winnerDiv = $('#winner');
	var winnerDisplay = $('#winner-data');
	winnerDisplay.html('The winner is ' + winner + '!!!');
	toggleElementVisibility(winnerDiv, 'on');
}

function bindCellClick() {
	$('.boatfight_gamecell').click(function(){
		var availableShots = parseInt(document.getElementById('available-shots').value);
		var isAvailable = $(this).hasClass('available');
		var isPending = $(this).hasClass('pending');
		var isUnavailable = $(this).hasClass('hit') || $(this).hasClass('miss') || $(this).hasClass('local') || $(this).hasClass('filled');
		if (isAvailable && availableShots > 0) {
			$(this).removeClass('available');
			$(this).addClass('pending');
			availableShots -= 1;
			document.getElementById('available-shots').value = availableShots;
			document.getElementById('available-shots-display').innerHTML = availableShots;
		} else if (isPending) {
			$(this).addClass('available');
			$(this).removeClass('pending');
			availableShots += 1;
			document.getElementById('available-shots').value = availableShots;
			document.getElementById('available-shots-display').innerHTML = availableShots;
		}
		if (availableShots == 0) {
			$('button#fire').removeAttr('disabled');
		} else {
			$('button#fire').prop('disabled', true);
		}
	});
}

function bindFireClick() {
	var fireUrl = $('input#boatfight-fire-url').val();
	$('button#fire').click(function(){
		postData = getShotsFired('pending');
		doAsyncPost(fireUrl, postData);
		endTurn();
	});
}

function initiateTurn(gameData) {
	var availableShots = gameData.player.availableShots;
	document.getElementById('available-shots').value = availableShots;
	var gameStats = document.getElementById('game-stats');
	gameStats.innerHTML = '';

	var gameStatsHeader = document.createElement('div');
	gameStatsHeader.setAttribute('class', 'game-stats_header');
	gameStatsHeader.innerHTML = "It's your turn!"

	var gameStatShots = document.createElement('div')
	gameStatShots.innerHTML = 'You have <span id="available-shots-display">' + availableShots + '</span> shots left';
	
	gameStats.append(gameStatsHeader);
	gameStats.append(gameStatShots);

	toggleOpponentBoard('on');
	togglePlayerBoard('off');
}

function endTurn() {
	$('div.pending').each(function(){
		$(this).removeClass('pending');
	});
	toggleOpponentBoard('off');
	togglePlayerBoard('on');
}

function setUpBoard(setUpUrl) {
	var setupData = {};
	$.ajax({
		method: 'GET',
		url: setUpUrl,
		dataType: 'json',
		async: false,
		success: function (gameSetup) {
			for (var boatType of Object.keys(gameSetup.boats)){
				var cacheIndex = 1;
				for (var positionIndex of Object.keys(gameSetup.boats[boatType].positions)){
					var position = gameSetup.boats[boatType].positions[positionIndex];
					var targetID = position.xPos + '-' +position.yPos;
					var boatSquare = $('#' + targetID);
					boatSquare.addClass('filled');
					boatSquare.attr('data-boat-type', boatType);
					var cacheImageID = boatType + '-' + cacheIndex;
					var divImage = getImageFromCache(cacheImageID);
					boatSquare.html(divImage);
					cacheIndex += 1;
				}
			}
			if(gameSetup.player.isCurrentPlayer) {
				initiateTurn(gameSetup);
			} else {
				toggleOpponentBoard('off');
				togglePlayerBoard('on');
			}
			setupData = gameSetup;
		}
	});
	return setupData;
}

function updateShots(shots, targetBoard, className, imageClassName) {
	for (var coordinateIndex of Object.keys(shots)){
		var xPos = shots[coordinateIndex][0];
		var yPos = shots[coordinateIndex][1];
		var targetDiv = $(targetBoard).find('#' + + xPos + '-' + yPos);
		if (!targetDiv.hasClass(className)) {
			targetDiv.addClass(className);
			if (targetDiv.hasClass('filled')) {
				targetDiv.removeClass('filled');
			}
		}
		if (imageClassName) {
			targetDiv.find('img').addClass(imageClassName);
		}
	}
}

function updateOpponentShots(opponentShots) {
	updateShots(opponentShots.hits, 'div#boatfightboard_player', 'hit', 'boat-part_hit');
	updateShots(opponentShots.misses, 'div#boatfightboard_player', 'missed', false);
	updateShots(opponentShots.sunk, 'div#boatfightboard_player', 'sunk', 'boat-part_sunk');
}

function updatePlayerShots(playerShots) {
	updateShots(playerShots.hits, 'div#boatfightboard_opponent', 'hit', false);
	updateShots(playerShots.misses, 'div#boatfightboard_opponent', 'missed', false);
	updateShots(playerShots.sunk, 'div#boatfightboard_opponent', 'sunk', false);
}

function updateGame(gameData, turnInitiated) {
	updatePlayerShots(gameData.playerShots);
	updateOpponentShots(gameData.opponentShots);
	if(gameData.gameStatus == 'over') {
		toggleWinner(gameData.winner);
	} else {
		if(gameData.player.isCurrentPlayer && !turnInitiated) {
			initiateTurn(gameData);
			turnInitiated = true;
		} else if (!gameData.player.isCurrentPlayer) {
			toggleOpponentBoard('off');
			togglePlayerBoard('on');
			document.getElementById('available-shots').value = gameData.player.availableShots;
			turnInitiated = false;
		}
	}
	return turnInitiated;
}
$(document).ready(function playGame(){ 
	var setUpUrl = $('input#boatfight-setup-url').val();
	var statusUrl = $('input#boatfight-status-url').val();
	var setupData = setUpBoard(setUpUrl);
	bindCellClick();
	bindFireClick();

	if (setupData.gameStatus == 'over') {
		var autoRefresh = false;
		$.ajax({
			method: 'GET',
			url: statusUrl,
			dataType: 'json',
			success: function (gameData) {
				updateGame(gameData);
			}
		});
	} else {
		var autoRefresh = true;
	}

	if (autoRefresh) {
		var turnInitiated = false;
		var gameLoop = window.setInterval(function startGameLoop(){
			$.ajax({
				method: 'GET',
				url: statusUrl,
				dataType: 'json',
				success: function (gameData) {
					turnInitiated = updateGame(gameData, turnInitiated);
				}
			});
		}, 1000)
	}
});
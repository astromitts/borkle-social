function togglePlayerBoard(visibility) {
	return visibility;
}

function toggleOpponentBoard(visibility) {
	var playerTools = $('#current-turn-tools');
	toggleElementVisibility(playerTools, visibility);
	return visibility;
}

function toggleWinner(gameData) {
	var winnerDiv = $('#winner');
	var winnerDisplay = $('#winner-data');
	var displayHTML = 'The winner is ' + gameData.winner + '!!!';
	if (gameData.lossType == 'conceded') {
		displayHTML += '<br />' + gameData.loser + ' conceded the game :(';
	} else {
		displayHTML += '<br />' + gameData.loser + ' lost all their ships :(';
	}
	winnerDisplay.html(displayHTML);
	toggleElementVisibility(winnerDiv, 'on');
}

function bindCellClick() {
	$('.boatfight_gamecell').click(function(){

		var gameType = document.getElementById('game-type').value;
		var availableShots = parseInt(document.getElementById('available-shots').value);
		var isAvailable = $(this).hasClass('available');
		var isPending = $(this).hasClass('pending');
		var isUnavailable = $(this).hasClass('hit') || $(this).hasClass('miss') || $(this).hasClass('local') || $(this).hasClass('filled');
		if (isAvailable && availableShots > 0) {
			$(this).removeClass('available');
			$(this).addClass('pending');
			availableShots -= 1;
			document.getElementById('available-shots').value = availableShots;
			if (gameType == 'salvo') {
				document.getElementById('available-shots-display').innerHTML = availableShots;
			}
		} else if (isPending) {
			$(this).addClass('available');
			$(this).removeClass('pending');
			availableShots += 1;
			document.getElementById('available-shots').value = availableShots;
			if (gameType == 'salvo') {
				document.getElementById('available-shots-display').innerHTML = availableShots;
			}
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
	var gameType = document.getElementById('game-type').value;

	var gameStats = document.getElementById('game-stats');
	gameStats.innerHTML = '';

	var gameStatsHeader = document.createElement('div');
	gameStatsHeader.setAttribute('class', 'game-stats_header');
	gameStatsHeader.innerHTML = "It's your turn!"
	gameStats.append(gameStatsHeader);
	
	if (gameType == 'salvo') {
		var availableShots = gameData.player.availableShots;
		document.getElementById('available-shots').value = availableShots;
		var gameStatShots = document.createElement('div')
		gameStatShots.innerHTML = 'You have <span id="available-shots-display">' + availableShots + '</span> shots left';
		gameStats.append(gameStatShots);
	} else {
		var availableShots = 1;
	}

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

function revealSunkShips(sunkShips) {
	sunkShips.forEach(function revealSunkShip(ship){
		var cacheIndex = 1;
		var orientation = ship.orientation;
		var boatType = ship.display.label;
		ship.coordinates.forEach(function revealShipPart (position){
			var targetID = position.x + '-' +position.y;
			var boatSquare = $('#boatfightboard_opponent #' + targetID);
			if (!boatSquare.hasClass('filled')) {
				boatSquare.addClass('filled');
			}
			if (boatSquare.find('img').length == 0) {
				boatSquare.attr('data-boat-type', boatType);
				var cacheImageID = boatType + '-' + cacheIndex;
				var divImage = getImageFromCache(cacheImageID);
				if (orientation == 'vertical') {
					var classList = 'boat-part boat-part_vertical';
				} else {
					var classList = 'boat-part';
				}
				divImage.className = classList;
				boatSquare.html(divImage);
			}
			cacheIndex += 1;
		});
	});
}

function setUpBoard(setUpUrl) {
	var setupData = {};
	$.ajax({
		method: 'GET',
		url: setUpUrl,
		dataType: 'json',
		async: false,
		success: function (gameSetup) {
			gameSetup.boats.forEach(function placeBoat(boat){
				var cacheIndex = 1;
				boat.coordinates.forEach(function placeBoatCoordinate(coordinate){
					var targetID = coordinate.x + '-' +coordinate.y;
					var boatSquare = $('#boatfightboard_player #' + targetID);
					var boatType = boat.display.label;
					boatSquare.addClass('filled');
					boatSquare.attr('data-boat-type', boatType);
					var cacheImageID = boatType + '-' + cacheIndex;
					var divImage = getImageFromCache(cacheImageID);
					boatSquare.html(divImage);
					cacheIndex += 1;
				});

			});
			revealSunkShips(gameSetup.sunkShips);

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

function updateShots(shots, targetBoard) {
	shots.forEach(function revealShot(shot){
		var xPos = shot.x;
		var yPos = shot.y;
		var className = shot.status;
		var targetDiv = $(targetBoard).find('#' + + xPos + '-' + yPos);
		if (!targetDiv.hasClass(className)) {
			targetDiv.addClass(className);
			if (targetDiv.hasClass('filled')) {
				targetDiv.removeClass('filled');
			}
		}
	});
}

function updateOpponentShots(opponentShots) {
	updateShots(opponentShots, 'div#boatfightboard_player');
}

function updatePlayerShots(playerShots) {
	updateShots(playerShots, 'div#boatfightboard_opponent');
}

function updateGame(gameData, turnInitiated) {
	updatePlayerShots(gameData.playerShots);
	updateOpponentShots(gameData.opponentShots);
	revealSunkShips(gameData.sunkShips);
	if(gameData.gameStatus == 'over') {
		toggleWinner(gameData);
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

	var manualRefresh = false;

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
		var autoRefresh = !manualRefresh;
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
					if (gameData.gameStatus == 'over') {
						clearInterval(gameLoop);
					}
				}
			});
		}, 1000)
	}

	if (manualRefresh) {
		var manualRefreshDiv = $('div#manual-refresh');
		toggleElementVisibility(manualRefreshDiv, 'on');
		$('button#manual-refresh').click(function doManualRefresh(){
			$.ajax({
				method: 'GET',
				url: statusUrl,
				dataType: 'json',
				success: function (gameData) {
					turnInitiated = updateGame(gameData, turnInitiated);
					if (gameData.gameStatus == 'over') {
						clearInterval(gameLoop);
					}
				}
			});
		});
	}
});
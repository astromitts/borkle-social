var boardHeight = [6, 5, 4, 3, 2, 1];
var totalTiles = 42;

function getDiagnalAxisEast(baseTileX, baseTileY) {
	/*  Return all coordinates that are along the NE axis of Base X and Base Y
		The max of X is 7
		the max of Y is 6

		if we get 6, 4
		we return
		7, 3
	*	6, 4
		5, 5
		4, 6
	*/
	var eastAxisDivs = {}
	eastAxisDivs[baseTileX] = [baseTileX, baseTileY];

	var yInc = 1;
	for (var i = baseTileX+1; i <= 7; i++) {
		if (baseTileY - yInc > 0) {
			eastAxisDivs[i] = [i, baseTileY - yInc];
		}
		yInc ++;
	}

	var yInc = 1;
	for (var i = baseTileX-1; i > 1; i--) {
		if (baseTileY + yInc < 7) {
			eastAxisDivs[i] = [i, baseTileY + yInc];
			yInc ++;
		}
	}

	return eastAxisDivs;
}

function getDiagnalAxisWest(baseTileX, baseTileY) {
	/*  Return all coordinates that are along the NW axis of Base X and Base Y
		The max of X is 7
		the max of Y is 6

		if we get 5, 4 
		we return
		2, 1
	    3, 2
		4, 3
	*   5, 4
		6, 5
		7, 6

	*/
	var westAxisDivs = {}
	westAxisDivs[baseTileX] = [baseTileX, baseTileY];

	var yInc = 1;
	for (var i = baseTileX+1; i <= 7; i++) {
		if (i <= 7) {
			westAxisDivs[i] = [i, baseTileY + yInc];
		}
		yInc ++;
	}

	var yInc = 1;
	for (var i = baseTileX-1; i > 1; i--) {
		if (baseTileY - yInc > 0) {
			westAxisDivs[i] = [i, baseTileY - yInc];
			yInc ++;
		}
	}

	return westAxisDivs;
}

function getVerticalAxis(baseTileX, baseTileY) {
	var yAxisDivs = {};
	yAxisDivs[0] = []
	var idx = 1;
	for (var i = 6; i >= 1; i--) {
	    yAxisDivs[idx] = [baseTileX, i];
	    idx++;
	}
	return yAxisDivs;
}

function getHorizontalAxis(baseTileX, baseTileY) {
	var xAxisDivs = {};
	xAxisDivs[0] = [];
	var idx = 1;
	for (var i = 7; i >= 1; i--) {
		var slotID = i + '-' + baseTileY;
		var thisDiv = $('#' + slotID);
	    xAxisDivs[i] = [i, baseTileY];
	    idx++;
	}
	return xAxisDivs;
}

function getConsecutiveFillsForAxis(axis) {
	var numInRow = 0;
	var consecutiveSlots = [];
	var currentConsecutiveRun = [];
	var previousSlotFilled = false;
	for (var idx of Object.keys(axis)){
		var axisSet = axis[idx];
		var thisX = axisSet[0];
		var thisY = axisSet[1];
		var divId = '#' + thisX + '-' + thisY;
		var thisDiv = $(divId);
		var isFilledByPlayer = thisDiv.find('.circle').hasClass('circle_filled__local_player');
		if(isFilledByPlayer && previousSlotFilled) {
			currentConsecutiveRun.push([thisX, thisY]);
			previousSlotFilled = true;
		} else if (isFilledByPlayer && !previousSlotFilled) {
			var currentConsecutiveRun = [];
			currentConsecutiveRun.push([thisX, thisY]);
			previousSlotFilled = true;
		} else {
			if (currentConsecutiveRun.length >= 4) {
				consecutiveSlots.push(currentConsecutiveRun);
			}
			var currentConsecutiveRun = [];
			previousSlotFilled = false;
		}
	}
	if (currentConsecutiveRun.length >= 4) {
		consecutiveSlots.push(currentConsecutiveRun);
	}
	return consecutiveSlots;
}

function checkAxisGroups(axisGroups){
	var winningDivs = [];
	axisGroups.forEach(function(axisSets){
		winningDivsForAxis = getConsecutiveFillsForAxis(axisSets);
		winningDivsForAxis.forEach(function (axisSets){
			axisSets.forEach(function (axisSet){
				winningDivs.push(axisSet)
			});
		});
	});
	return winningDivs;
}

function checkForFourInARow(baseTileX, baseTileY) {
	var winningRows = [];
	if ($('.circle_filled__local_player').length >= 4){
		var horizontalAxis = getHorizontalAxis(baseTileX, baseTileY);
		var vertixalAxis = getVerticalAxis(baseTileX, baseTileY);
		var eastAxis = getDiagnalAxisEast(baseTileX, baseTileY);
		var westAxis = getDiagnalAxisWest(baseTileX, baseTileY);

		var axisGroups = [
			horizontalAxis,
			vertixalAxis,
			eastAxis,
			westAxis,
		];
		var winningRows = checkAxisGroups(axisGroups);
	}
	return winningRows;
}

function updateBoard(xPos, yPos) {
	var updateUrl = $('#updateboard-url').val();
	var playerID = $('#gameplayer-id').val();
	var postData = {
		'x': xPos,
		'y': yPos,
		'gameplayer_id': playerID,
	}
	doAsyncPost(updateUrl, postData);
}

function sendWinnerData(winningRows) {
	var playerID = $('#gameplayer-id').val();
	var endGameUrl = $('#endgame-url').val();
	var postData = {}
	var postCoordStrings = []
	winningRows.forEach(function(winningRow){
		var xPos = winningRow[0];
		var yPos = winningRow[1];

		postData['winningCell_' + xPos + '-' + yPos] = 'win';
		postCoordStrings.push('{"x": ' + xPos + ', "y": ' + yPos + '}');
	});
	postCoordString = '{"coordinates": [' + postCoordStrings.join(",") + ']}'
	postData['coordinates'] = postCoordString
	doNonAsyncPost(endGameUrl, postData);
}

function sendDrawData() {
	var endGameUrl = $('#draw-url').val();
	var postData = {};
	doNonAsyncPost(endGameUrl, postData);
}

function getBottomMostOpenSpot(xPos) {
	placementDiv = null;
	boardHeight.forEach(function(yPos){
		var possiblePlacementDiv = $('#' + xPos + '-' +yPos);
		if(!possiblePlacementDiv.find('.circle').hasClass('circle_filled')) {
			if(placementDiv == null) {
				placementDiv = possiblePlacementDiv;
			}
		}
	});
	return placementDiv;
}

function animateTileRed(tile) {
	var circle = tile.find('.circle');
	circle.animate(
		{ 
			backgroundColor: "#FF7A7A",
		}, 50
	);
}

function animateTileWhite(tile) {
	var circle = tile.find('.circle');
	circle.animate(
		{ 
			backgroundColor: "#FFFFFF",
		}, 50
	);
}

function placeFinalTile(finalTile) {

	var finalCirlce = finalTile.find('.circle');

	finalCirlce.animate(
		{ 
			backgroundColor: "#FF7A7A",
		}, 100
	);

	var testAnimationInterval = setInterval(function () {
		if (! $.timers.length) {
			clearInterval(testAnimationInterval);
			finalCirlce.addClass('circle_filled');
			finalCirlce.addClass('circle_filled__local_player')
			target.removeClass('selected');
			var finalXpos = parseInt(finalTile.attr('data-x'));
			var finalYpos = parseInt(finalTile.attr('data-y'));
			var remainingTiles = updateRemainingTiles();
			var winningRows = checkForFourInARow(finalXpos, finalYpos);
			if ( winningRows.length > 0 ) {
				sendWinnerData(winningRows);
			} else if (remainingTiles == 0) {
				sendDrawData();
			}
			updateBoard(finalTile.attr('data-x'), finalTile.attr('data-y'));
		}
	}, 25);
}

function bindDropTile() {
	$('button#drop-tile').click(function(){
		target = $('.selected');
		if (target.length == 1 ){
			var xPos = target.parent().attr('data-x');
			var potentialTiles = [];
			var finalTile = null;
			for (var idx of Object.keys(boardHeight)){
				var yPos = boardHeight[idx];
				var potentialTile = $('#' + xPos + '-' +yPos);
				var potentialTileCircle = potentialTile.find('.circle');
				if ( !potentialTileCircle.hasClass('circle_filled') && finalTile == null ) {
					finalTile = potentialTile;
				} else if (!potentialTileCircle.hasClass('circle_filled')) {
					potentialTiles.push(potentialTile);
				}
			}
			if (finalTile != null && potentialTiles.length > 0) {
				$('.circle_pending').removeClass('circle_pending');
				potentialTiles.reverse();
				var animatedTiles = 0;
				potentialTiles.forEach(function(tile){
					var flashedRed = false;
					var testAnimationInterval = setInterval(function () {
				        if (! $.timers.length) { // any page animations finished
							if (!flashedRed) {
								animateTileRed(tile);
								flashedRed = true;
							} else {
					            clearInterval(testAnimationInterval);
					            animateTileWhite(tile);
					            animatedTiles += 1;
					            if (animatedTiles == potentialTiles.length) {
					            	placeFinalTile(finalTile);
					            }
							}
				        }
				    }, 25);
				});

			} else if(finalTile != null) {
				placeFinalTile(finalTile);
			}
		}
	});
}

function bindSelectDropPosition() {
	$('#boxdots-tile-positioner .circle').click(function selectDropPosition(){
		var isActivePlayer = $(this).parent().parent().hasClass('boxdots-positioner_active');
		if (isActivePlayer) {
			var xPos = $(this).parent().attr('data-x');
			$('.circle_pending').each(function(){
				$(this).removeClass('circle_pending');
			});

			$('.selected').each(function(){
				$(this).removeClass('selected');
			});
			if(!$(this).hasClass('selected')) {
				var possiblePlacement = getBottomMostOpenSpot(xPos);
				if (possiblePlacement != null) {
					$(this).addClass('selected');
					possiblePlacement.find('.circle').addClass('circle_pending');
					//$(this).bind('click', bindDropTile($(this)));
				}
			} 
		}
	});
}

function updateRemainingTiles() {
	var placedTilesOnBoardCount = $('.circle_filled').length;
	var currentPlacedTilesCount = parseInt($('#remaining-tiles').val());
	var currentRemainingTiles = totalTiles - placedTilesOnBoardCount;
	if (placedTilesOnBoardCount != currentRemainingTiles) {
		$('#remaining-tiles').val(currentRemainingTiles);
	}
	return currentRemainingTiles;
}

function refreshBoard(gameData) {
	var localPlayerId = parseInt($('#gameplayer-id').val());
	var tileClass;
	for (var idx of Object.keys(gameData.placedTiles)){
		var coordinates = gameData.placedTiles[idx];
		var tilePlayer = parseInt(coordinates.filledById);
		if (tilePlayer == localPlayerId) {
			tileClass = 'circle_filled__local_player';
		} else {
			tileClass = 'circle_filled__remote_player';
		}
		var circle = $('#' + coordinates.x + '-' + coordinates.y).find('.circle');
		circle.addClass('circle_filled');
		circle.addClass(tileClass);
	}
	var tilePlacer = $('#boxdots-positioner-row');
	var gameTools = $('#drop-tile');
	if ( gameData.isCurrentPlayer == true && gameData.gameStatus == 'active' ) {
		if (!tilePlacer.hasClass('boxdots-positioner_active')) {
			tilePlacer.addClass('boxdots-positioner_active');
			tilePlacer.removeClass('boxdots-positioner_inactive');
			toggleElementVisibility(gameTools, 'on');
		}
	} else {
		if (tilePlacer.hasClass('boxdots-positioner_active')) {
			tilePlacer.removeClass('boxdots-positioner_active');
			tilePlacer.addClass('boxdots-positioner_inactive');
			toggleElementVisibility(gameTools, 'off');
		}
	}
	updateRemainingTiles();
}

function displayWinnerData(winnerName, winnerCoordinates) {
	var winnerDiv = $('#winner');
	var gameToolsDiv = $('#game-tools');
	var playAgainDiv = $('#play-again');
	$('span.winner-name').each(function(){
		$(this).html(winnerName);
	});
	$('span#winner-count').html(gameData.winningCoordinates.length);
	toggleElementVisibility(winnerDiv, 'on');
	toggleElementVisibility(playAgainDiv, 'on');
	toggleElementVisibility(gameToolsDiv, 'off');
	for (var idx of Object.keys(gameData.winningCoordinates)){
		var coordinates = gameData.winningCoordinates[idx];
		$('div#' + coordinates.x + '-' + coordinates.y).addClass('boxdots-gameboard_winner');
	}
}

function displayDrawData() {
	var drawDiv = $('#draw');
	var gameToolsDiv = $('#game-tools');
	var playAgainDiv = $('#play-again');
	toggleElementVisibility(gameToolsDiv, 'off');
	toggleElementVisibility(drawDiv, 'on');
	toggleElementVisibility(playAgainDiv, 'on');
}


$(document).ready(function playGame(){
	bindSelectDropPosition();
	bindDropTile();

	var refreshUrl = $('#getboard-url').val();
	var autoRefresh = true;

	if (autoRefresh) {
		var gameLoop = window.setInterval(function startGameLoop(){
				$.ajax({
					method: 'GET',
					url: refreshUrl,
					dataType: 'json',
					success: function successFunction(data) {
						gameData = data;
						refreshBoard(gameData);
						if (gameData.gameStatus == 'over') {
							if (gameData.winner) {
								displayWinnerData(gameData.winner, gameData.winningCoordinates);
							} else {
								displayDrawData();
							}
							clearInterval(gameLoop);
						}
					}
				});
		}, 1000);
	} else {
		refreshBoard();
	}
});
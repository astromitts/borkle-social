function getXOptions(xPos, yPos, boatSize) {
	return Array(boatSize).fill().map((_, i) => parseInt(xPos + i) + '-' + yPos);
}

function getYOptions(xPos, yPos, boatSize) {
	return Array(boatSize).fill().map((_, i) => xPos + '-' + parseInt(yPos + i));
}

function getActiveBoatBase() {
	var baseElements = document.getElementsByClassName('pending');
	if (baseElements.length > 0) {
		return $('#' + baseElements[0].id);
	}
	return null;
}

function directionValid(axisOptions) {
	var optionWorks = true;
	axisOptions.forEach(function checkXOptions(optionId) {
		var potentialDiv = $('div#' + optionId);
		if (potentialDiv.length == 0 || potentialDiv.hasClass('filled')) {
			optionWorks = false;

		}
	});
	return optionWorks;
}

function clearPendingCells() {
	$('.pending').each(function(){
		$(this).removeClass('pending');
		$(this).html('');
	});
}

function clearFlippedCells(previousDivCells) {
	previousDivCells.forEach(function(cellID){
		previousDiv = $('#' + cellID);
		previousDiv.addClass('boatfight_gamecell__available');
		previousDiv.attr('data-orientation', '');
		previousDiv.attr('data-boat-size', '');
		previousDiv.attr('data-boat-type', '');
		previousDiv.html('');
	});
}

function fillBoatPlacement(axisOptions, boatSize, orientation, boatType) {
	clearPendingCells();
	var cacheIndex = 1;
	axisOptions.forEach(function fillCells(optionId) {
		var potentialDiv = $('div#' + optionId);
		potentialDiv.addClass('pending');
		potentialDiv.removeClass('boatfight_gamecell__available');
		potentialDiv.attr('data-orientation', orientation);
		potentialDiv.attr('data-boat-size', boatSize);
		potentialDiv.attr('data-boat-type', boatType);
		var cacheImageID = boatType + '-' + cacheIndex;
		var divImage = getImageFromCache(cacheImageID);
		if (orientation == 'y') {
			divImage.setAttribute('class', 'boat-part boat-part_vertical');
		}
		potentialDiv.html(divImage);
		cacheIndex += 1;
	});
}

function flipBoatOrientation(orientationBase) {
	var currentOrentation = orientationBase.attr('data-orientation');
	var boatSize = parseInt(orientationBase.attr('data-boat-size'));
	var boatType = orientationBase.attr('data-boat-type');
	var yPos = parseInt(orientationBase.attr('data-y'));
	var xPos = parseInt(orientationBase.attr('data-x'));
	var xAxisOptions = getXOptions(xPos, yPos, boatSize);
	var yAxisOptions = getYOptions(xPos, yPos, boatSize);
	if (currentOrentation == 'x') {
		var boatPlaced = placeBoat(orientationBase, boatSize, 'y', boatType);
		if ( boatPlaced ) {
			xAxisOptions.shift();
			clearFlippedCells(xAxisOptions);
		}
	} else {
		var boatPlaced = placeBoat(orientationBase, boatSize, 'x', boatType);
		if ( boatPlaced ) {
			yAxisOptions.shift();
			clearFlippedCells(yAxisOptions);
		}
	}
	
}

function bindFlipBoatOrientation(target) {
	target.click(function() {
		orientationBase = getActiveBoatBase();
		flipBoatOrientation(orientationBase);
	});
}

function _boatIsAlreadyPlaced(boatType) {
	var boatIsPlaced = false;
	$('.pending').each(function(){
		var pendingID = $(this).attr('data-boat-type');
		boatIsPlaced = boatType == pendingID;
	});
	return boatIsPlaced;
}

function flashInvalidDivs(axisDivs) {
	axisDivs.forEach(function checkXOptions(optionId) {
		$('div#' + optionId).stop().css("background-color", "red")
		.animate({ backgroundColor: "#FFFFFF"}, 500);
	});
}

function placeBoat(orientationBase, boatSize, priorityOrientation, boatType) {
	var yPos = parseInt(orientationBase.attr('data-y'));
	var xPos = parseInt(orientationBase.attr('data-x'));
	var xAxisOptions = getXOptions(xPos, yPos, boatSize);
	var yAxisOptions = getYOptions(xPos, yPos, boatSize);
	var xOptionWorks = directionValid(xAxisOptions);
	var yOptionWorks = directionValid(yAxisOptions);
	var boatIsAlreadyPlace = _boatIsAlreadyPlaced(boatType);
	var boatPlaced = false;

	if (priorityOrientation == 'x') {	
		if (xOptionWorks) {
			fillBoatPlacement(xAxisOptions, boatSize, 'x', boatType);
			boatPlaced = true;
		} else if (yOptionWorks && !boatIsAlreadyPlace) {
			fillBoatPlacement(yAxisOptions, boatSize, 'y', boatType);
			boatPlaced = true;
		} else {
			flashInvalidDivs(xAxisOptions);
		}
	} else {
		if (yOptionWorks) {
			fillBoatPlacement(yAxisOptions, boatSize, 'y', boatType);
			boatPlaced = true;
		} else if (xOptionWorks && !boatIsAlreadyPlace) {
			fillBoatPlacement(xAxisOptions, boatSize, 'x', boatType);
			boatPlaced = true;
		} else {
			flashInvalidDivs(yAxisOptions);
		}
	}

	return boatPlaced;
}

function bindPlaceBoat() {
	$('.boatfight_gamecell__available').click(function displayPlacementOptions(){
		var selectedBoat = $('.boatfight-boats_boat__selected');
		if (selectedBoat.length > 0) {
			orientationBase = getActiveBoatBase();
			if (orientationBase != null) {
				priorityOrientation = orientationBase.attr('data-orientation');
			} else {
				priorityOrientation = 'x';
			}
			var boatSize = parseInt(selectedBoat.attr('data-boat-size'));
			var boatType = selectedBoat.attr('id');
			var boatPlaced = placeBoat($(this), boatSize, priorityOrientation, boatType);
			if ( boatPlaced ) {
				// selectedBoat.removeClass('boatfight-boats_boat__selected');
				var gameBoard = $('#boatfight_placement-board');
				gameBoard.removeClass('boatfight_placement-board__active');
				showShipButtons();
			}
		}
	});
}

function bindSelectBoatFromQueue() {
	$('.boat-to-place').click(function selectBoat(){
		if ($(this).hasClass('boatfight-boats_boat__selected')) {
			clearPendingCells();
			$(this).removeClass('boatfight-boats_boat__selected');
		} else if (!$(this).hasClass('boat-placed')) {
			clearPendingCells();
			$('.boatfight-boats_boat__selected').removeClass('boatfight-boats_boat__selected');
			$(this).addClass('boatfight-boats_boat__selected');
		}
	});
}

function bindSelectBoatFromBoard(target) {
	target.click(function selectBoat(){
		if( $(this).hasClass('filled')) {
			hideReadyButton();
			$('.boat-to-place').removeClass('boatfight-boats_boat__selected');
			var clickedBoatType = $(this).attr('data-boat-type');
			var queuedBoat = $('#' + clickedBoatType);
			$('.filled').each(function(){
				var placedBoatType = $(this).attr('data-boat-type');
				if (placedBoatType == clickedBoatType) {
					$(this).removeClass('filled');
					$(this).addClass('pending');
				}
			});
			queuedBoat.removeClass('boat-placed');
			queuedBoat.addClass('boatfight-boats_boat__selected');
			showShipButtons();
		}
	});
}

function hideReadyButton() {
	var readyDiv = $('#ready-button');
	toggleElementVisibility(readyDiv, 'off');
	showShipButtons();
}

function showReadyButton() {
	var readyDiv = $('#ready-button');
	toggleElementVisibility(readyDiv, 'on');
	hideShipButtons();
}

function hideShipButtons() {
	var lockDiv = $('#lock-button');
	toggleElementVisibility(lockDiv, 'off');
	
	var flipDiv = $('#flip-button');
	toggleElementVisibility(flipDiv, 'off');
}

function showShipButtons() {
	var lockDiv = $('#lock-button');
	toggleElementVisibility(lockDiv, 'on');
	
	var flipDiv = $('#flip-button');
	toggleElementVisibility(flipDiv, 'on');
}

function bindLockBoat() {
	$('#lock').click(function(){
		var selectedBoatBase = getActiveBoatBase();
		var boatTypeID = selectedBoatBase.attr('data-boat-type');
		$('div#' + boatTypeID).removeClass('boat-to-place');
		$('div#' + boatTypeID).addClass('boat-placed');
		$('div#' + boatTypeID).removeClass('boatfight-boats_boat__selected');
		$('.pending').each(function(){
			$(this).removeClass('pending');
			$(this).addClass('filled');
			$(this).addClass('boatfight_gamecell__locked');
			bindSelectBoatFromBoard($(this));
		});
		hideShipButtons();

		if( $('.boat-placed').length == 5) {
			showReadyButton();
		}
	});
}

function bindSubmitBoatPlacements() {
	$('#ready').click(function(){
		postData = getGameBoardData('filled');
		var setUpUrl = $('input#boatfight-setup-url').val();
		$.ajax({
			method: 'POST',
			url: setUpUrl,
			dataType: 'json',
			data: postData,
			async: false,
			success: function () {
				location.reload();
			}
		});
	});
}


$(document).ready(function setupGameBoard(){ 
	bindSelectBoatFromQueue();
	bindPlaceBoat();
	bindFlipBoatOrientation($('button#flip'));
	bindLockBoat();
	bindSubmitBoatPlacements();
});
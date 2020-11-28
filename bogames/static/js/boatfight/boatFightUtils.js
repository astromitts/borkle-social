
function getGameBoardData(targetClass) {
	var postData = {}
	var boatCounts = {
		'battleship': 0,
		'carrier': 0,
		'cruiser': 0,
		'submarine': 0,
		'destroyer': 0,
	}
	$('.' + targetClass).each(function(){
		var boatType = $(this).attr('data-boat-type');
		var boatCount = boatCounts[boatType] + 1;

		var xPos = $(this).attr('data-x');
		var yPos = $(this).attr('data-y');
		xField = boatType + '_' + boatCount + '_x';
		yField = boatType + '_' + boatCount + '_y';
		postData[xField] = xPos;
		postData[yField] = yPos;
		boatCounts[boatType] = boatCount;
	});
	return postData;
}

function getShotsFired(targetClass) {
	var postData = {}
	var shotInt = 1;
	$('.' + targetClass).each(function(){
		var xPos = $(this).attr('data-x');
		var yPos = $(this).attr('data-y');
		postData['shot_' + shotInt + '_x'] = xPos;
		postData['shot_' + shotInt + '_y'] = yPos;
		shotInt += 1
	});
	return postData;
}
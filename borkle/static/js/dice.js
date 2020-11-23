function rollDice(diceAmount) {
	diceValues = [1,2,3,4,5,6];
	rolledDice = []
	for (const x of Array(diceAmount).keys()) {
		rolledDice.push(diceValues[Math.floor(Math.random() * diceValues.length)]);
	}
	return rolledDice;
}

function valueCounts(diceSet) {
	var counts = {
		1: 0,
		2: 0,
		3: 0,
		4: 0,
		5: 0,
		6: 0,
	}
	diceSet.forEach(function(value){
		var strVal = value.toString();
		counts[strVal]++;
	});
	return counts;
}

function isAllOfKind(diceSet, expectedCount) {
	if (diceSet.length != expectedCount) {
		return false;
	}

	var initial_val = diceSet[0];
	var _isAllOfKind = true;
	diceSet.forEach(function(value){
		if (value === initial_val == false) {
			_isAllOfKind = false;
		}
	});
	return _isAllOfKind;
}

function isAllFives(diceSet) {
	var _isAllFives = true;
	diceSet.forEach(function(value){
		if (value != 5) {
			_isAllFives = false;
		}
	});
	return _isAllFives;
}

function isAllOnes(diceSet) {
	var _isAllOnes = true;
	diceSet.forEach(function(value){
		if (value != 1) {
			_isAllOnes = false;
		}
	});
	return _isAllOnes;
}

function hasFivesOrOnes(diceSet) {
	var _hasFivesOrOnes = false;
	diceSet.forEach(function(value){
		if (value == 5 || value == 1) {
			_hasFivesOrOnes = true;
		}
	});
	return _hasFivesOrOnes;
}

function isAllFivesOrOnes(diceSet) {
	var _isAllFivesOrOnes = true;
	diceSet.forEach(function(value){
		if (value != 5 && value != 1) {
			_isAllFivesOrOnes = false;
		}
	});
	return _isAllFivesOrOnes;
}

function isThreeOfKind(diceSet) {
	return isAllOfKind(diceSet, 3);
}

function isFourOfKind(diceSet) {
	return isAllOfKind(diceSet, 4);
}

function isFiveOfKind(diceSet) {
	return isAllOfKind(diceSet, 5);
}

function isSixOfKind(diceSet) {
	return isAllOfKind(diceSet, 6);
}

function isStraight(diceSet) {
	var uniqueValues = []
	diceSet.forEach(function(value){
		if (!uniqueValues.includes(value)){
			uniqueValues.push(value);
		}
	});
	return uniqueValues.length == 6;
}

function isFourAndPair(diceSet) {
	var counts = valueCounts(diceSet);
	number_of_fours = 0
	number_of_twos = 0
	for (var diceValue of Object.keys(counts)) {
		var occurances = counts[diceValue];
		if(!occurances in [0, 2, 4]) {
			return false;
		}
		if ( occurances == 2 ) {
			number_of_twos++;
		} else if ( occurances == 4 ) {
			number_of_fours++;
		}
	};
	return number_of_fours == 1 && number_of_twos == 1;
}

function isThreePairs(diceSet) {
	var counts = valueCounts(diceSet);
	number_of_twos = 0
	for (var diceValue of Object.keys(counts)) {
		var occurances = counts[diceValue];
		if(!occurances in [0, 2]) {
			return false;
		}
		if ( occurances == 2 ) {
			number_of_twos++;
		}
	};
	return number_of_twos == 3;
}

function isTwoTriples(diceSet) {
	var counts = valueCounts(diceSet);
	number_of_threes = 0
	for (var diceValue of Object.keys(counts)) {
		var occurances = counts[diceValue];
		if(!occurances in [0, 3]) {
			return false;
		}
		if ( occurances == 3 ) {
			number_of_threes++;
		}
	};
	return number_of_threes == 2;
}

function hasThreeOrMoreKind(diceSet) {
	counts = valueCounts(diceSet);
	_hasThreeOrMoreKind = false;
	for (var diceValue of Object.keys(counts)) {
		var occurances = counts[diceValue];
		if (occurances >= 3) {
			_hasThreeOrMoreKind = true;
		}
	};
	return _hasThreeOrMoreKind;
}

function scoreDiceSet(diceSet) {
	var score = {}
	score.locked = false;
	score.scoreType = null;
	score.scoreValue = null;
	score.hasScore = false;
	score.scorableValues = [];

	if (diceSet.length == 0){
		return score;
	}
	if (isFourAndPair(diceSet)) {
		score.scoreType = 'Four of a kind and a pair';
		score.scoreValue = 2500;
		score.hasScore = true;
		score.scorableValues = diceSet;
	} else if (isTwoTriples(diceSet)) {
		score.scoreType = 'Two triples';
		score.scoreValue = 1500;
		score.hasScore = true;
		score.scorableValues = diceSet;
	} else if (isStraight(diceSet)) {
		score.scoreType = 'Straight';
		score.scoreValue = 1500;
		score.hasScore = true;
		score.scorableValues = diceSet;
	} else if (isThreePairs(diceSet)) {
		score.scoreType = 'Three pairs';
		score.scoreValue = 1500;
		score.hasScore = true;
		score.scorableValues = diceSet;
	} else if (isSixOfKind(diceSet)) {
		score.scoreType = 'Six of a kind';
		score.scoreValue = 3000;
		score.hasScore = true;
		score.scorableValues = diceSet;
	} else if (isFiveOfKind(diceSet)) {
		score.scoreType = 'Five of a kind';
		score.scoreValue = 2000;
		score.hasScore = true;
		score.scorableValues = diceSet;
	} else if (isFourOfKind(diceSet)) {
		score.scoreType = 'Four of a kind';
		score.scoreValue = 1000;
		score.hasScore = true;
		score.scorableValues = diceSet;
	} else if (isThreeOfKind(diceSet)) {
		score.scoreType = 'Three of a kind';
		if(isAllOnes(diceSet)) {
			score.scoreValue = 300;
		} else {
			score.scoreValue = diceSet[0] * 100;
		}
		score.hasScore = true;
		score.scorableValues = diceSet;
	} else if (isAllFivesOrOnes(diceSet)) {
		score.scoreValue = 0;
		diceSet.forEach(function(value){
			if (value == 1) {
				score.scoreValue = score.scoreValue + 100;
			} else if (value == 5) {
				score.scoreValue = score.scoreValue + 50;
			}
		});
		if(isAllOnes(diceSet)) {
			score.scoreType = 'Ones'
		} else if (isAllFives(diceSet)) {
			score.scoreType = 'Fives'
		} else {
			score.scoreType = 'Ones and fives'
		}
		score.hasScore = true;
		score.scorableValues = diceSet;
	} else {
		score.scoreType = 'Borkle';
		score.scoreValue = 0;
		score.hasScore = false;
		score.scorableValues = null;
	}
	return score;
}

function hasScore(diceSet) {
	testScore = scoreDiceSet(diceSet);
	_hasScore = false;
	if ( testScore.hasScore == false) {
		if (hasFivesOrOnes(diceSet) == true) {
			_hasScore = true;
		} else if (hasThreeOrMoreKind(diceSet) == true) {
			_hasScore = true;
		}
	} else {
		_hasScore = true;
	}
	return _hasScore;
}

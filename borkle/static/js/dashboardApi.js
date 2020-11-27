function _gameTitle(game) {
	var gameTitle = document.createElement('h5');
	gameTitle.setAttribute('class', 'card-title');
	gameTitle.innerHTML = '<span class="codename">codename</span>' + game.codeName;
	return gameTitle;
}

function _gameLink(game) {
	var gameLink = document.createElement('a');
	gameLink.setAttribute('href', game.link);

	var gameButton = document.createElement('button');
	gameButton.setAttribute('class', 'game-btn');
	gameButton.innerHTML = 'Go to Game';

	gameLink.append(gameButton);

	return gameLink;
}

function _cancelLink(game) {
	var gameLink = document.createElement('a');
	gameLink.setAttribute('href', game.cancelLink);

	var gameButton = document.createElement('button');
	gameButton.setAttribute('class', 'float-right game-btn game-btn_red');
	gameButton.innerHTML = 'Cancel Game';

	gameLink.append(gameButton);

	return gameLink;
}

function _joinLink(game) {
	var gameLink = document.createElement('a');
	gameLink.setAttribute('href', game.joinLink);

	var gameButton = document.createElement('button');
	gameButton.setAttribute('class', 'game-btn');
	gameButton.innerHTML = 'Join Game';

	gameLink.append(gameButton);

	return gameLink;
}

function _declineLink(game) {
	var gameLink = document.createElement('a');
	gameLink.setAttribute('href', game.declineLink);

	var gameButton = document.createElement('button');
	gameButton.setAttribute('class', 'float-right game-btn game-btn_red');
	gameButton.innerHTML = 'Decline Game';

	gameLink.append(gameButton);

	return gameLink;
}

function _activeGamePlayer(player, game) {
	var playerInfoDiv = document.createElement('div');
	var playerInfo = document.createElement('h6');
	playerInfo.setAttribute('id', game.codeName + '-' +player.username+ '-body');
	if ( player.isCurrentPlayer ) {
		playerInfo.innerHTML = player.username + "'s turn";
		playerInfo.setAttribute('class', 'activeplayer card-subtitle mb-2');
	} else {
		playerInfo.innerHTML = player.username;
		playerInfo.setAttribute('class', 'activeplayer card-subtitle mb-2 muted');
	}
	playerInfo.setAttribute('id', 'activeplayer_' + player.username);
	return playerInfo;
}

function _pendingGamePlayer(player, game) {
	var playerInfo = document.createElement('h6');
	playerInfo.setAttribute('id', game.codeName + '-' +player.username+ '-body');
	if ( player.ready ) {
		playerInfo.innerHTML = player.username + ": ready!";
	} else {
		playerInfo.innerHTML = player.username + ": waiting";
	}
	playerInfo.setAttribute('class', 'activeplayer card-subtitle mb-2');
	playerInfo.setAttribute('id', 'pendingplayer_' + player.username);
	return playerInfo;
}

function activeGameCard(game) {
	var gameTitle = _gameTitle(game);
	var gameLink = _gameLink(game);
	var gameCard = document.createElement('div');
	gameCard.setAttribute('class', 'card active');
	gameCard.setAttribute('id', game.codeName);
	//gameCard.setAttribute('style', 'width: 18rem;')

	var cardBody = document.createElement('div');
	cardBody.setAttribute('class', 'card-body');
	cardBody.append(gameTitle);

	for (var index of Object.keys(game.players)) { 
		player = game.players[index];
		var playerInfo = _activeGamePlayer(player, game);
		cardBody.append(playerInfo);
	}
	cardBody.append(gameLink);

	gameCard.append(cardBody);

	return gameCard;
}

function updatePlayerInfo(game, playerInfoFunc) {
	for (var index of Object.keys(game.players)) { 
		player = game.players[index];
		var playerInfoId = game.codeName + '-' +player.username+ '-body';
		var currentPlayerInfo = document.getElementById(playerInfoId);
		var playerInfo = playerInfoFunc(player, game);
		if ( currentPlayerInfo.innerHTML != playerInfo.innerHTML ) {
			currentPlayerInfo.innerHTML = playerInfo.innerHTML;
		}
	}
}

function pendingGameCard(game) {
	var gameTitle = _gameTitle(game);
	var gameLink = _gameLink(game);
	var cancelLink = _cancelLink(game);
	var gameCard = document.createElement('div');
	gameCard.setAttribute('class', 'card pending');
	gameCard.setAttribute('id', game.codeName);
	//gameCard.setAttribute('style', 'width: 18rem;')

	var cardBody = document.createElement('div');
	cardBody.setAttribute('class', 'card-body');
	cardBody.append(gameTitle);

	for (var index of Object.keys(game.players)) { 
		player = game.players[index];
		var playerInfo = _pendingGamePlayer(player, game);
		cardBody.append(playerInfo);
	}
	cardBody.append(gameLink);
	cardBody.append(cancelLink);

	gameCard.append(cardBody);

	return gameCard;
}

function invitedGameCard(game) {
	var gameTitle = _gameTitle(game);
	var joinLink = _joinLink(game);
	var declineLink = _declineLink(game);
	var gameCard = document.createElement('div');
	gameCard.setAttribute('class', 'card');
	gameCard.setAttribute('id', game.codeName);
	//gameCard.setAttribute('style', 'width: 18rem;')

	var cardBody = document.createElement('div');
	cardBody.setAttribute('class', 'card-body invited');
	cardBody.append(gameTitle);

	for (var index of Object.keys(game.players)) { 
		player = game.players[index];
		var playerInfo = _pendingGamePlayer(player, game);
		cardBody.append(playerInfo);
	}
	cardBody.append(joinLink);
	cardBody.append(declineLink);

	gameCard.append(cardBody);

	return gameCard;
}

function placeActiveCard(activeGame) {
	var GameDiv = document.getElementById('active-games');
	var existingCard = document.getElementById(activeGame.codeName);
	var activeGame = activeGameCard(activeGame);
	GameDiv.append(activeGame);
}

function placePendingCard(pendingGame) {
	var GameDiv = document.getElementById('pending-games');
	var existingCard = document.getElementById(pendingGame.codeName);	
	var thisGameCard = pendingGameCard(pendingGame);
	GameDiv.append(thisGameCard);
}

function placeInvitationCard(invitedGame) {
	var GameDiv = document.getElementById('invited-games');
	var existingCard = document.getElementById(invitedGame.codeName);
	var thisGameCard = invitedGameCard(invitedGame);
	GameDiv.append(thisGameCard);
}

function placeCard(game) {
	if (game.dashboardStatus == 'active' ) {
		placeActiveCard(game);
	} else if (game.dashboardStatus == 'pending' ) {
		placePendingCard(game);
	} else if (game.dashboardStatus == 'invited' ) {
		placeInvitationCard(game);
	}

}

function setCards(dashboardData) {
	for (var index of Object.keys(dashboardData.games)) {
		var thisGame = dashboardData.games[index];

		var thisGameCard = document.getElementById(thisGame.codeName);
		if (thisGameCard == undefined || thisGameCard == null){
			placeCard(thisGame);
		} else {
			var hasNewStatus = !thisGameCard.className.includes(thisGame.dashboardStatus);
			if (hasNewStatus) {
				thisGameCard.remove();
				placeCard(thisGame);
			} else {
				if (thisGame.dashboardStatus == 'active' ) {
					updatePlayerInfo(thisGame, _activeGamePlayer);
				} else {
					updatePlayerInfo(thisGame, _pendingGamePlayer);
				}
			}
		}	
	}
}

function refreshDashboard() {
	var refreshUrl = $('input#refreshurl').val();
	$.ajax({
		method: 'GET',
		url: refreshUrl,
		dataType: 'json',
		success: function(dashboardData) {
			setCards(dashboardData);
		}
	});
}


$(document).ready(function dashboard(){
	var autoRefresh = true;

	if (autoRefresh) {
		var gameLoop = window.setInterval(function startGameLoop(){
			refreshDashboard();

		}, 1000);
	} else {
		refreshDashboard();
	}
});
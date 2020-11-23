

function getPlayerCardData() {
	var refreshGameInfoUrl = $('input#api-scorecardsetup-url').val();
	var playerCardData = doNonAsyncGet(refreshGameInfoUrl);
	for (var playerName of Object.keys(playerCardData.scorecards)) {
		var cardData = playerCardData.scorecards[playerName];
		var nextPlayerName = cardData.next_player_card;
		var prevPlayerName = cardData.previous_player_card;
		var playerCardDiv = document.getElementById('score-card-log_' + playerName);
		if ( nextPlayerName != null ) {
			playerCardDiv.setAttribute('data-next-player', 'score-card-log_' + nextPlayerName);
		}		
		if ( prevPlayerName != null ) {
			playerCardDiv.setAttribute('data-prev-player', 'score-card-log_' + prevPlayerName);
		}
	}
}

function bindScoreCardNav() {
	$('button.scorecard-nav').click(function(){
		var directionTargetAttr = $(this).attr('data-target-attr');
		var currentCard = $('.scorecard-nav_active').first();
		var displayNextId = currentCard.attr(directionTargetAttr);
		var displayNext = $('#' + displayNextId);
		currentCard.removeClass('scorecard-nav_active');
		currentCard.addClass('hidden');
		displayNext.addClass('scorecard-nav_active');
		displayNext.removeClass('hidden');
	});
}
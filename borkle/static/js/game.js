function show_error(message) {
	$('div#messages').html(message);
	$('div#messages').css('visibility', '');
}

function clear_error() {
	$('div#messages').html('');
	$('div#messages').css('visibility', 'hidden');
}

function save_selection(saveScoreUrl, selectionSet) {
	$.ajax({
		method: 'POST',
		url: saveScoreUrl,
		dataType: 'json',
		data: selectionSet,
		success: function (data) {
			refresh_gameboard();
		}
	});
}

function bind_undo_selection() {
	$('button#undo-selection').click(function(){
		var $targetUrl = $(this).attr('target-url');
		$.ajax({
			method: 'GET',
			url: $targetUrl,
			data: {},
			dataType: 'json',
			success: function (data) {
				refresh_gameboard();
			}
		});
	});
}

function hide_rollbutton(){
	$('button#rolldice').css('visibility', 'hidden');
}

function bind_select_dice() {
	$('img.dice_selectable').click(function(){
		var $diceID = $(this).attr('id');
		if ($(this).hasClass('dice_selected')) {
			$(this).removeClass('dice_selected');
			$('input#' + $diceID).val('')
		} else {
			$(this).addClass('dice_selected');
			$('input#' + $diceID).val('selected')
		}
	});
}

function bind_make_selection() {

	$('button#makeselection').click(function(){
		var $checkScoreUrl = $(this).attr('data-checkscore-url');
		var $saveScoreUrl = $(this).attr('data-set-selection-url');
		var selectedDiceIds = {}
		$('input.selected-dice').each(function(){
			var $isSelected = $(this).val() == 'selected';
			if ( $isSelected ) {
				selectedDiceIds[($(this).attr('id'))] = 'select';
			}
		});
		clear_error();
		$.ajax({
			method: 'POST',
			url: $checkScoreUrl,
			dataType: 'json',
			data: selectedDiceIds,
			success: function (data) {
				if( data['has_score']) {
					save_selection($saveScoreUrl, selectedDiceIds);
				} else {
					show_error('That is not a scoring selection, try again.')
				}
			}
		});
	});
}

function bind_roll_dice() {
	$('button#rolldice').click(function(){
		var $targetUrl = $(this).attr('data-target-url');
		var $targetDivId = $(this).attr('data-target-div');
		$.ajax({
			method: 'GET',
			url: $targetUrl,
			dataType: 'html',
			success: function (data) {
				$( "div#" + $targetDivId ).html( data );
				var $borkle = $('input#borkle').val() == 'True';
				if (!$borkle) {
					bind_select_dice();
					bind_make_selection();
				}
				hide_rollbutton();
			}
		});
	});
}

function checkIfCurrentPlayer() {
	var $checkStatusUrl = $('input#status-check-url').val();
	$.ajax({
		method: 'GET',
		url: $checkStatusUrl,
		dataType: 'json',
		success: function (data) {
			if(data['is_current_player'] == true) {
				return true;
			}
		}
	});
	return false;
}

function refresh_gameboard(checkReload) {
	$('div.autorefresh').each(function(){
		var $targetUrl = $(this).attr('data-target-url');
		var $targetDivId = $(this).attr('id');
		$.ajax({
			method: 'GET',
			url: $targetUrl,
			dataType: 'html',
			success: function (data) {
				$( "div#" + $targetDivId ).html( data );
				if($targetDivId == 'gameboard') {
					bind_roll_dice();
				} else if($targetDivId == 'diceboard'){
					bind_make_selection();
					bind_select_dice();
					bind_undo_selection();
				}
			}
		});
	});
}

$(document).ready(function(){
	var $autoRefresh = $('input#autorefresh').val() == 'True';
	refresh_gameboard(false);
	if ($autoRefresh) {
		window.setInterval(function(){
			var $checkHistoryUrl = $('input#checkhistory').val();
			$.ajax({
				method: 'GET',
				url: $checkHistoryUrl,
				dataType: 'json',
				success: function (data) {
					var isChanged = data['changed'] == true;
					var isOver = data['status'] == 'over';
					if (isOver) {
						window.location.replace(data['game_history_url']);
					}
					if( isChanged ) {
						var $checkStatusUrl = $('input#status-check-url').val();
						var isCurrentPlayer = false;
						$.ajax({
							method: 'GET',
							url: $checkStatusUrl,
							dataType: 'json',
							success: function (data) {
								isCurrentPlayer = data['is_current_player'] == true;
								if(isCurrentPlayer) {
									location.reload();
								}else{
									refresh_gameboard(true);
								}
							}
						});
					}
				}
			});
		}, 3000);
	}
});
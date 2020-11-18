function refresh_dashboard() {
	var $refreshUrl = $('input#refreshurl').val();
	$.ajax({
		method: 'GET',
		url: $refreshUrl,
		dataType: 'html',
		success: function (data) {
			$('div#dashboard-games').html(data);
		}
	});
}

$(document).ready(function(){
	autorefresh = true;
	if (autorefresh) {
		window.setInterval(function(){
			refresh_dashboard();
		}, 3000);
	}
});
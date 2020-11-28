function toggleElementVisibility(target, visibility) {
	if (visibility == 'on' && target.hasClass('hidden')) {
		target.removeClass('hidden');
	} else if (visibility == 'off' && !target.hasClass('hidden')) {
		target.addClass('hidden');
	}
}

function doAsyncPost(targetUrl, postData) {
	$.ajax({
		method: 'POST',
		url: targetUrl,
		dataType: 'json',
		data: postData,
	});
}

function doNonAsyncGet(targetUrl) {
	var resultData;
	$.ajax({
		method: 'GET',
		url: targetUrl,
		dataType: 'json',
		async: false,
		success: function successFunction(data) {
			resultData = data;
		}
	});
	return resultData;
}

function getImageFromCache(imageId) {
	var imgSource = document.getElementById(imageId);
	var imgClone = imgSource.cloneNode();
	return imgClone;
}

function isAllNull(testList) {
	var nullCount = 0;
	testList.forEach(function checkIfNull(val){
		if(val == null){
			nullCount++;
		}
	});
	return nullCount == testList.length;
}

function stripNulls(diceSet) {
	var nonNulls = [];
	diceSet.forEach(function removeNull(val) {
		if(val == null == false){
			nonNulls.push(val);
		}
	});
	return nonNulls;
}
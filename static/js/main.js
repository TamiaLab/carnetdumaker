$(document).ready(function () {
    $(window).scroll(function () {
        if ($(this).scrollTop() > 50) {
            $('#back-to-top').fadeIn();
        } else {
            $('#back-to-top').fadeOut();
        }
    });
    // scroll body to 0px on click
    var back_to_top = $('#back-to-top')
    back_to_top.click(function () {
        $('#back-to-top').tooltip('hide');
        $('body,html').animate({
            scrollTop: 0
        }, 800);
        return false;
    });
    back_to_top.tooltip('show');
});

$(document).ready(function () {
    $(window).scroll(function () {
        if ($(this).scrollTop() > 50) {
            $('#beta-alert').fadeOut();
        } else {
            $('#beta-alert').fadeIn();
        }
    });
});

$(".spoiler").each(function(index) {
	var t = $(this);
	t.hide();
	var l = $('<div><input type="button" value="Voir le texte caché"></div>');
	l.insertBefore($(this));
	l.click(function() {
		t.show();
		$(this).hide();
	});
});

$(".ispoiler").each(function(index) {
	var t = $(this);
	t.hide();
	var l = $('<input type="button" value="Voir le texte caché">');
	l.insertBefore($(this));
	l.click(function() {
		t.show();
		$(this).hide();
	});
});
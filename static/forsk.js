$(function() {
    $("ul.people li a").click(function(e) {
        var $this = $(this),
            circle = $this.data('mnemonic') || '',
            circleName = $this.data('name') || '',
            nick = $this.parent().find('span').html();
        e.preventDefault();
        $.get('/attend?nick=' + nick + '&circle=' + circle, function(result, status) {
            if (result) {
                $this.parent()
                    .find('span')
                        .css({opacity: "0.5"})
                    .end()
                    .find('a')
                        .remove()
                    .end()
                    .append('<em>' + circle + '</em>') // TODO: Ajax-unattend()
                    ;
            } else {
                console.debug('Bad args.');
            }
        });
    });
    
    $(".unattender").live('click', function(e) {
        var $this = $(this),
            circle = $this.data('circle') || '',
            nick = $this.data('nick') || '';
        e.preventDefault();
        $.get('/unattend?nick=' + nick + '&circle=' + circle, function(result, status) {
            window.location.href=window.location.href;
        });
        
        
    });
	$('.box h3').click(function() {
		$(this)
			.parent()
			.find('ul')
				.show('slow')
			.end()
			.find('form')
				.show('slow')
			.end();
	});
});

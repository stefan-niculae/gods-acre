$("document").ready(main);

function main() {
    // Enable tooltips
    $('[data-toggle="tooltip"]').tooltip({
        placement: 'bottom',
    }); 
    
    // Enable popovers
    $('[data-toggle="popover"]').popover();
    dismissPopoversOnOusideClick();
 
    ownerBuiltItalics();
}

function dismissPopoversOnOusideClick() {
    $('body').on('click', function (e) {
        //only buttons
        if ($(e.target).data('toggle') !== 'popover'
            && $(e.target).parents('.popover.in').length === 0) { 
            $('[data-toggle="popover"]').popover('hide');
        }
        //buttons and icons within buttons
        /*
        if ($(e.target).data('toggle') !== 'popover'
            && $(e.target).parents('[data-toggle="popover"]').length === 0
            && $(e.target).parents('.popover.in').length === 0) { 
            $('[data-toggle="popover"]').popover('hide');
        }
        */
    });
}

// TODO move this to a separate js that executes only on this page
function ownerBuiltItalics() {
    $('td').each(function() {
        // HACK
        if ($(this).text().trim().substring(0, 1) == '*') {
            $(this).text($(this).text().replace('\*', ''));
            $(this).addClass('italic');
        }
    });
}
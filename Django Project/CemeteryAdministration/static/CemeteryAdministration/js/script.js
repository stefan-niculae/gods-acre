$("document").ready(main);

function main() {
    // Enable tooltips
    $('[data-toggle="tooltip"]').tooltip({
        placement: 'bottom',
    });
    $('[data-toggle="tooltip-top"]').tooltip({
        placement: 'top',
    });
    
    // Enable popovers
    $('[data-toggle="popover"]').popover();
    
    dismissPopoversOnOusideClick();
    
    $('.navbar-toggle ').on('click', function() {
        console.log('clicked navbar toogle');
    });
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

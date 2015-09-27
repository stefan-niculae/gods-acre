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
    
//    dismissPopoversOnOusideClick();
    
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

var focused;

// TODO input validation
$(  
// Find all editable content.
$('[contenteditable]')

    // When you click on item, record into data("initialText") content of this item.
    .focus(function() {
        $(this).data('initialText', $(this).html().trim());
        focused = $(this);
    })

    // Unfocus
    .blur(function() {
        focused = undefined;
        if ($(this).data('initialText') !== $(this).html().trim()) {
            ajaxPost('/save', 
            {
                'entity':   $(this).attr('entity'),
                'db_id':    $(this).attr('db-id'),
                'field':    $(this).attr('field'),
                'data':     $(this).html().trim()
            },
            function(status) {
                console.log(status);
            });
        }
    })
);

// Enter and escape on editable content
$(document).keyup(function(e) {
    function unfocus() {
        focused.blur();
        window.getSelection().removeAllRanges();
    }
    
    // Enter pressed
    if (e.which == '13' && focused != undefined)
        unfocus();
    
    // Escape pressed
    if (e.which == '27' && focused != undefined) {
        // Reset to content before editing
        focused.html(focused.data('initialText'));
        unfocus();
    }
});

// General search binding
$(function() {
    
// Disable page reloading
$('.general-search form').submit(function(e) {
    // TODO || e.which and other things, on other functions too
    // TODO trim input value
    search($(e.target).children('input').val());
    return false;
});

});

function search(criteria) {
    matched = $('td:contains(' + criteria + ')').closest('tr');
    // TODO recolor (stripped table) rows when hiding/showing
    matched.show();
    $('tbody tr').not(matched).hide();
}


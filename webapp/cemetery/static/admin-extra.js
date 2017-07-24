document.addEventListener("DOMContentLoaded", function() {
    var tabs     = document.getElementsByClassName('changeform-tabs-item')
    var contents = document.getElementsByClassName('module')

    for (var selectedIndex = 0; selectedIndex < tabs.length; selectedIndex++)
        tabs[selectedIndex].onclick = function (selectedIndex) {
            return function() {
                console.log('clicked', selectedIndex)

                // remove 'selected' class from all tabs and contents
                for (var i = 0; i < tabs.length; i++) {
                    tabs    [i].classList.remove('selected')
                    contents[i].classList.remove('selected')
                }

                // set 'selected' only desired tab and content
                tabs    [selectedIndex].classList.add('selected')
                contents[selectedIndex].classList.add('selected')
            }
        }(selectedIndex)
})

function askConfirmationIfWiping() {
    var wiping_checked = document.forms.import.wipe_beforehand.checked
    if (wiping_checked)
        // TODO: internationalization https://docs.djangoproject.com/en/1.11/topics/i18n/translation/#internationalization-in-javascript-code
        return confirm('Are you sure you want to delete everything from the database before importing?')
    return true
}

function toggleStatus(box, status) {
    var checkboxes = document.querySelectorAll('.status-toggler.' + status + ' input[type="checkbox"]')
    for (var i = 0; i < checkboxes.length; i++)
        checkboxes[i].checked = box.checked

    var rows = document.getElementsByClassName('toggleable-row ' + status)
    var display = box.checked ? 'table-row' : 'none'
    for (i = 0; i < rows.length; i++)
        rows[i].style.display = display
}
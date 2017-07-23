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

    // TODO: toggle for sheet-wise fail, duplicate, add, selected
    // TODO: line-through for row-wise selected
})

function askConfirmationIfWiping(e) {
    var wiping_checked = document.forms.import.wipe_beforehand.checked
    if (wiping_checked)
        return confirm('Are you sure you want to delete everything from the database before importing?')
    return true
}

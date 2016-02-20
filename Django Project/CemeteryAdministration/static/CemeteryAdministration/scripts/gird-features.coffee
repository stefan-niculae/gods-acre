$ ->
  jsGridInit()
  changeIcons()

jsGridInit = ->
  $("table").jsGrid

    width: "100%"
    # If set to 100% then the pager won't go lower when there are fewer rows to display (no content or last page)
    # But then filter clearing is glitchy and initial data loading doesn't work
    # height: "100%"

    # Field definitions
    fields: [
      {
        name: "parcel"
        title: "P"
        type: "text"
      },
      {
        name: "row"
        title: "R"
        type: "text"
      },
      {
        name: "column"
        title: "C"
        type: "text"
      },
      {
        name: "year"
        title: "Year"
        # It's actually a number, but when sending the data, the default for an empty number is zero
        # while the default for an empty text is the empty string
        # which IS contained in everything
        type: "text" # number

        align: "left"
        headercss: "left-aligned-header"
      },
      {
        name: "value"
        title: "Value"
        type: "text" # number

        align: "left"
        headercss: "left-aligned-header"
      },
      {
        name: "receiptNumber"
        title: "RNumber"
        type: "text" # number

        headercss: "left-aligned-header"
      },
      {
        name: "receiptYear"
        title: "RYear"
        type: "text" # number

        headercss: "left-aligned-header"
      },
      {
        type: "control"
        editButton: false # hide the explicit edit button (rows are clickable to edit anyway)
        modeSwitchButton: true # TODO add a tutorial to teach what this this button is doing
      }
    ]

    controller: jsGridController

    # Features
    heading:    true
    filtering:  true
    inserting:  true
    editing:    true
    selecting:  true
    sorting:    true
    paging:     true
    #pageLoading: true #?
    autoload:   true #?

    # Paging
    pageSize: 5 # TODO testing: set to an appropriate value
    pageButtonCount: 3
    # Whitespace must be around a keyword because they're part of the delimiter
    pagerFormat: "{first} {prev} {pages} {next} {last} ( {itemCount} results )"
    pagePrevText: "<i class=\"fa fa-chevron-left\"></i>"
    pageNextText: "<i class=\"fa fa-chevron-right\"></i>"
    pageFirstText: "First"
    pageLastText: "Last"

caseInsensitive = true

jsGridController =
  loadData: (filter) ->
    d = $.Deferred()

    $.ajax(
      type: "GET"
      url: "/revenue_jsgrid/api"
      data: filter
    ).done (result) ->
      d.resolve $.map result, (item) ->
        $.extend item.fields, id: item.pk

    d.promise()


changeIcons = ->
#  console.log "TODO: change icons"
  # TODO jsgrid-clear-filter-button to <i class="fa fa-ban"></i>
  # delete button
  # search button
  # add plus button

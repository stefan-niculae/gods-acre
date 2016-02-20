$ ->
  paymentsTable = $ "#payments-table"
  initJsGrid paymentsTable
  # addTableSuperHeaders paymentsTable
  changeIcons()

initJsGrid = (table) ->
  table.jsGrid

    width: "100%"
    # If set to 100% then the pager won't go lower when there are fewer rows to display (no content or last page)
    # But then filter clearing is glitchy and initial data loading doesn't work
    # height: "100%"

    # Field definitions
    fields: [
      {
        name: "parcel"
        title: "Spot Parcel"
        type: "text"
      },
      {
        name: "row"
        title: "Spot Row"
        type: "text"
      },
      {
        name: "column"
        title: "Spot Column"
        type: "text"
      },
      {
        name: "year"
        title: "Year Paid"
        # It's actually a number, but when sending the data, the default for an empty number is zero
        # while the default for an empty text is the empty string
        # which IS contained in everything
        # TODO make a custom field that acts as a number and on empty sends ''?
        type: "text" # number

        align: "left"
        headercss: "left-aligned-header"
      },
      {
        name: "value"
        title: "Paid Amount"
        type: "text" # number

        align: "left"
        headercss: "left-aligned-header"
      },
      {
        name: "receiptNumber"
        title: "Receipt Nr"
        type: "text" # number

        headercss: "left-aligned-header"
      },
      {
        name: "receiptYear"
        title: "Receipt Year"
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
    pageSize: 25 # TODO add this in preferences
    pageButtonCount: 5
    # Whitespace must be around keywords because they're part of the delimiter
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


addTableSuperHeaders = (table) ->
  $ """
    <tr class="jsgrid-header-row super-header-row">
      <th colspan="3">Spot</th>
      <th colspan="2">Payment</th>
      <th colspan="2">Receipt</th>
    </tr>
  """
    .prependTo table


changeIcons = ->
#  console.log "TODO: change icons"
  # TODO jsgrid-clear-filter-button to <i class="fa fa-ban"></i>
  # delete button
  # search button
  # add plus button

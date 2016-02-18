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
        name: "id"
        title: "#" # displayed in header
        type: "number"
        editing: false
        width: "5%"
        css: "id-cell"
        headercss: "right-aligned-header"
      },
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
        type: "number"

        align: "left"
        headercss: "left-aligned-header"
      },
      {
        name: "value"
        title: "Value"
        type: "number"

        align: "left"
        headercss: "left-aligned-header"
      },
      {
        name: "receipt"
        title: "Receipt"
        type: "text"

        align: "left"
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
    pagerFormat: "{first} {prev} {pages} {next} {last} ( {pageIndex} of {pageCount} )"
    pagePrevText: "<i class=\"fa fa-chevron-left\"></i>"
    pageNextText: "<i class=\"fa fa-chevron-right\"></i>"
    pageFirstText: "First"
    pageLastText: "Last"

caseInsensitive = true

jsGridController =
  loadData: (filter) ->
    $.grep @.encashments, (encashment) ->
      (!filter.id || encashment.id == filter.id) and

      (!filter.parcel || encashment.parcel.contains(filter.parcel, caseInsensitive)) and
      (!filter.row || encashment.row.contains(filter.row, caseInsensitive)) and
      (!filter.column || encashment.column.contains(filter.column, caseInsensitive)) and

      (!filter.year || encashment.year == filter.year) and
      (!filter.value || encashment.value == filter.value) and

      (!filter.receipt || encashment.receipt.contains(filter.receipt, caseInsensitive))


  # TODO get data from the backend
  encashments: [
      {
          "column": "11B",
          "id": 0,
          "parcel": "3",
          "receipt": "14/2001",
          "row": "15C",
          "value": 105,
          "year": 2005
      },
      {
          "column": "5A",
          "id": 1,
          "parcel": "6A",
          "receipt": "16/1997",
          "row": "8C",
          "value": 165,
          "year": 1994
      },
      {
          "column": "2A",
          "id": 2,
          "parcel": "18A",
          "receipt": "20/1996",
          "row": "16",
          "value": 145,
          "year": 1996
      },
      {
          "column": "9A",
          "id": 3,
          "parcel": "11B",
          "receipt": "3/1986",
          "row": "11",
          "value": 115,
          "year": 1991
      },
      {
          "column": "3bis",
          "id": 4,
          "parcel": "5bis",
          "receipt": "8/2005",
          "row": "16C",
          "value": 160,
          "year": 2009
      },
      {
          "column": "2A",
          "id": 5,
          "parcel": "6C",
          "receipt": "8/2002",
          "row": "15bis",
          "value": 180,
          "year": 2007
      },
      {
          "column": "13bis",
          "id": 6,
          "parcel": "9B",
          "receipt": "9/2005",
          "row": "1bis",
          "value": 200,
          "year": 2004
      },
      {
          "column": "10B",
          "id": 7,
          "parcel": "11",
          "receipt": "6/2005",
          "row": "20",
          "value": 155,
          "year": 2004
      },
      {
          "column": "5bis",
          "id": 8,
          "parcel": "3",
          "receipt": "11/1995",
          "row": "8A",
          "value": 115,
          "year": 1991
      },
      {
          "column": "14B",
          "id": 9,
          "parcel": "6C",
          "receipt": "2/1995",
          "row": "14",
          "value": 170,
          "year": 2000
      },
      {
          "column": "1",
          "id": 10,
          "parcel": "7",
          "receipt": "1/2016",
          "row": "1",
          "value": 200,
          "year": 2015
      }
    ]

changeIcons = ->
#  console.log "TODO: change icons"
  # TODO jsgrid-clear-filter-button to <i class="fa fa-ban"></i>
  # delete button
  # search button
  # add plus button

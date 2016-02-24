$ ->
  paymentsTable = $ ".jsgrid"
  initJsGrid paymentsTable
  # addTableSuperHeaders paymentsTable
  changeIcons()


# TODO remove the debugging @
@tableConfigs =
  # TODO widths
  spotFields: [
    {
      name: "parcel"
      title: "Parcel"
      type: "text"
    },
    {
      name: "row"
      title: "Row"
      type: "text"
    },
    {
      name: "column"
      title: "Column"
      type: "text"
    }
  ]

  controlFields: [
    {
      type: "control"
      editButton: false # hide the explicit edit button (rows are clickable to edit anyway)
      modeSwitchButton: true # TODO add a tutorial to teach what this this button is doing
    }
  ]

  payments:
    url: "/payments/api/"

    fields: [
      {
        name: "year"
        title: "Year Paid"
        type: "number"

        align: "left" # FIXME
        headercss: "left-aligned-header"
      },
      {
        name: "value"
        title: "Paid Amount"
        type: "number"

        align: "left"
        headercss: "left-aligned-header"
      },
      {
        name: "receiptNumber"
        title: "Receipt Nr"
        type: "number"

        headercss: "left-aligned-header"
      },
      {
        name: "receiptYear"
        title: "Receipt Year"
        type: "number"

        headercss: "left-aligned-header"
      }
    ]

  burials:
    url: "/burials/api/"

    fields: [
      {
        name: "firstName"
        title: "First Name"
        type: "text"
      },
      {
        name: "lastName"
        title: "Last Name"
        type: "text"
      },
      {
        name: "type"
        title: "Type"
        type: "select"

        items: [
          { Text: "", Value: "" },
          { Text: "Burial", Value: "bral" },
          { Text: "Exhumation", Value: "exhm" },
        ]
        textField: "Text"
        valueField: "Value"

        align: "left"
        headercss: "left-aligned-header"
      },
      {
        name: "year" # TODO date instead of year here?
        title: "Year"
        type: "number"
      },
      {
        name: "note"
        title: "Notes"
        type: "text" # TODO make a big editing text field type
      }
    ]

  maintenance:
    url: "/maintenance_jsgrid/api/"

    # TODO add phone number to fields too?
    fields: [
      {
        name: "year"
        title: "Year"
        type: "number"
      },
      {
        name: "isKept"
        title: "Kept"
        type: "checkbox"

        headercss: "left-aligned-header"
      },
      { # TODO autocomplete these when creating two
        name: "firstName"
        title: "First Name"
        type: "text"

        inserting: false
        editing: false
      },
      {
        name: "lastName"
        title: "Last Name"
        type: "text"

        inserting: false
        editing: false
      },
    ]

  ownerships:
    url: "/ownerships_jsgrid/api/"

    fields: [
      {
        name: "firstName"
        title: "First Name"
        type: "text"
      },
      {
        name: "lastName"
        title: "Last Name"
        type: "text"
      },
      {
        name: "phone"
        title: "Phone"
        type: "text"
      },
      {
        name: "deedNumber"
        title: "Deed Nr"
        type: "number"
      },
      {
        name: "deedYear"
        title: "Deed Year"
        type: "number"
      },
      {
        # TODO auto-generate these when editing/inserting
        name: "sharingSpots"
        title: "On Same Deed"
        type: "text"

        inserting: false
        editing: false
      },
      {
        name: "receiptNumber"
        title: "Receipt Nr"
        type: "number"
      },
      {
        name: "receiptYear"
        title: "Receipt Year"
        type: "number"
      },
      {
        name: "receiptValue"
        title: "Amount Paid"
        type: "number"
      }
    ]

  constructions:
    url: "/constructions_jsgrid/api/"

    fields: [
      {
        name: "constructionType"
        title: "Type"
        type: "select"

        items: [
          { Text: "", Value: "" },
          { Text: "Border", Value: "brdr" },
          { Text: "Tomb", Value: "tomb" },
        ]
        textField: "Text"
        valueField: "Value"

        align: "left"
        headercss: "left-aligned-header"
      },
      {
        name: "builder"
        title: "Builder"
        type: "text"
      },
      {
        name: "authorizationNumber"
        title: "Auth Nr"
        type: "number"
      },
      {
        name: "authorizationYear"
        title: "Auth Year"
        type: "number"
      },
      {
        # TODO auto-generate these when editing/inserting
        name: "sharingAuthorization"
        title: "On Same Auth"
        type: "text"

        inserting: false
        editing: false
      }
    ]


# TODO make page size (and modifiable) and results count always visible
initJsGrid = (table) ->

  configs = tableConfigs[table.attr "id"]

  table.jsGrid

    width: "100%"
    # If set to 100% then the pager won't go lower when there are fewer rows to display (no content or last page)
    # But then filter clearing is glitchy and initial data loading doesn't work
    # height: "100%"

    # Field definitions
    # TODO make this nicer
    fields: tableConfigs.spotFields.concat configs.fields, tableConfigs.controlFields

    controller:
      loadData: (filter) ->
        d = $.Deferred()

        # The default (when the input is empty) for a number is zero
        # But on the backend we search for containment and 0 is not contained in 5 but '' is contained in '5'
        # So we use this workaround to change before filtering every zero to the empty string ''
        # Warning: if the user wants to search for the actual number zero, every result will be shown!
        for key, val of filter
          if val is 0 && key.match /(number|year|value)$/i
            console.log "key = #{key}, val = #{val}"
            filter[key] = ''

        console.log "filter = #{JSON.stringify(filter, null, 2)}"

        $.ajax(
          type: "GET"
          url: configs.url
          data: filter
        )
        .done (result) ->
          # console.log JSON.stringify result, null, 2
          # TODO can't i put the id as a field from the db and this is no longer necessary?
          d.resolve $.map result, (item) ->
            $.extend item.fields, id: item.pk

        d.promise()

      insertItem: (item) ->
        # TODO autocomplete for spot P/R/C (and don't let something else be entered)
        # TODO autocomplete for receipt year/number (& show an indicator if you post on an existing receipt)
        $.ajax
          type: "POST"
          url: configs.url
          data: item

      updateItem: (item) ->
        # TODO tell the user whether a new spot is created or they entered an existing one
        $.ajax
          type: "PUT"
          url: "#{configs.url}#{item.id}"
          data: item

      deleteItem: (item) ->
        $.ajax
          type: "DELETE"
          url: "#{configs.url}#{item.id}"

    # Features
    heading:    true
    filtering:  true # TODO enter searches, esc clears
    inserting:  true # TODO validators
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

# External variables

tableWrapper = "example-table"
columnWidths = [1, 1, 1, 1, 2, 3, 3]





# Utils

sum = (arr) ->
  arr.reduce (prev, curr) -> prev + curr

printError = (format, args...) ->
  console.error s.sprintf format, args...





# Backgrid config & fetch

Encashment = Backbone.Model.extend {}
Encashments = Backbone.Collection.extend
  model: Encashment
  url: "encashments.json"

  # TODO pagination
#  # Initial pagination states
#  state:
#    pageSize: 10
#    sortKey: 'id'
#    order: 1
encashments = new Encashments()

cursorAtEndEditor = Backgrid.InputCellEditor.extend
  postRender: () ->
    val = this.$el.val()
    this.$el.focus().val("").val(val)

alignedIntegerCell = Backgrid.IntegerCell.extend
  className: "aligned-integer-cell"
  editor: cursorAtEndEditor

stringCell = Backgrid.StringCell.extend
  editor: cursorAtEndEditor

columns = [
  {
    name: "" # Required (but we don't need one on a select all column)
    cell: 'select-row' # Selecting individual rows
    headerCell: 'select-all' # Select all the rows on a page
    editable: false
    sortable: false
  }
  {
    name: 'id' # The key of the model attribute
    label: '#' # The name to display in the header
    editable: false # ID isn't editable
    cell: alignedIntegerCell.extend(
        orderSeparator: "" # No thousands separator for the ID
        className: "id-cell"
      )
    sortType: "toggle"
    direction: "ascending" # Data should come sorted by ID
  }
  {
    name: "parcel"
    label: "P"
    cell: stringCell
    sortType: "toggle"
  }
  {
    name: "row"
    label: "R"
    cell: stringCell
    sortType: "toggle"
  }
  {
    name: "column"
    label: "C"
    cell: stringCell
    sortType: "toggle"
  }
  {
    name: "year"
    label: "Year"
    cell: alignedIntegerCell.extend(
        orderSeparator: "" # No thousands separator for the year
        className: "year-cell"
      )
    sortType: "toggle"
  }
  {
    name: "value"
    label: "Value"
    cell: alignedIntegerCell
    sortType: "toggle"
  }
  {
    name: "receipt"
    label: "Receipt"
    cell: stringCell
    sortType: "toggle"
  }
  {
    name: "editing-buttons"
    label: ""
    formatter: _.extend {}, Backgrid.CellFormatter.prototype,
      fromRaw: () ->
        """
        <button class="btn btn-info duplicate"><i class="fa fa-files-o"></i></button>
        <button class="btn btn-danger  delete"><i class="fa fa-trash-o"></i></button>
        """
    cell: Backgrid.HtmlCell.extend(
      className: "editing-buttons-cell"
    )
    sortable: false
    editable: false
  }
]



# Initialize a new Grid instance
grid = new Backgrid.Grid
  columns: columns
  collection: encashments
  className: "backgrid table table-striped table-bordered table-condense table-hover"
  emptyText: "No data" # TODO better message for empty data (centered, and no highlight id header)

# Render grid and attack to DOM
$tableWrapper = $ "#" + tableWrapper
$tableWrapper.append grid.render().el

# TODO pagination
#var paginator = new Backgrid.Extension.Paginator({
#    // If you anticipate a large number of pages, you can adjust
#    // the number of page handles to show. The sliding window
#    // will automatically show the next set of page handles when
#    // you click next at the end of a window.
#    windowSize: 20, // Default is 10
#
#    // Used to multiple windowSize to yield a number of pages to slide,
#    // in the case the number is 5
#    slideScale: 0.25, // Default is 0.5
#
#    // Whether sorting should go back to the first page
#    goBackFirstOnSort: true, // Default is true
#
#    collection: encashments
#});
#
#$tableWrapper.append(paginator.render().el);

# Case-insensitive regex search on the client side
# by OR-ing the keywords in the search box
clientSideFilter = new Backgrid.Extension.ClientSideFilter
  collection: encashments
  placeholder: "Search" #TR
  # The model fields to search for matches
  fields: ["id", "parcel", "row", "column", "year", "value", "receipt"]
  # How long to wait after typing has stopped before searching can
  wait: 200

$tableWrapper.prepend clientSideFilter.render().el



# Fetch from the url
encashments.fetch
  reset: true
  success: () ->
    setColumnWidths tableWrapper, columnWidths

    setInitialSortedHighlight tableWrapper, columns, "id"
    setHighlightOnSort tableWrapper
    setClearSortingOnSearch tableWrapper
    addSortedIndicator tableWrapper

    setSearchIcons tableWrapper
    setSearchSize tableWrapper
    setSearchEscClear tableWrapper

    # TODO align buttons properly to the right
    addColumnFiltering tableWrapper
    addEntityForm tableWrapper, columnWidths

  error: (collection, response) ->
    printError "Fetching failed. Error response: %s.", response


# Bootstrap styling

bootstrapColumns = 12

addWidths = (elements, widths, colType) ->
  colType = "lg"
  for [elem, width] in _.zip elements, widths
    $(elem).addClass s.sprintf "col-%s-%d", colType, width

setColumnWidths = (tableWrapper, widths, colType) ->
  if sum(widths) != bootstrapColumns
    msg = "Total number of columns (%d) differs from total number of bootstrap columns (%d)."
    printError msg, sum widths, bootstrapColumns

  # Prepend with a zero to account for the SelectAll column
  # and append a zero to account for the editing buttons
  adjustedWidths = [0].concat widths
  adjustedWidths.push 0

  headers = $ "#" +  tableWrapper + " th"
  # Subtract one for the SelectAll column and one for the editing buttons column
  if headers.length - 2 != widths.length
      msg = "The number of columns (%d) differs from the number of headers (%d)."
      printError msg, widths.length, headers.length - 2

  addWidths headers, adjustedWidths, colType


repositionRow = (grid, oldIndex, newIndex) ->
  rows = grid.$el.find "tbody tr"
  n = rows.length

  if n is 0
    printError "Grid is empty"
    return

  if Math.abs(oldIndex) >= n or Math.abs(newIndex) > n
    printError "Index is larger than the number of rows"
    return

  # -1 becomes n - 1
  oldIndex = n + oldIndex if oldIndex < 0
  newIndex = n + newIndex if newIndex < 0

  toMove = rows.eq oldIndex
  aboveWhat = rows.eq newIndex
  toMove.insertBefore aboveWhat


highlightColumn = (tableWrapper, columnIndex) ->
  $ "##{tableWrapper} td:nth-child(#{columnIndex})"
    .addClass "sorted-col"


setInitialSortedHighlight = (tableWrapper, columns, idName) ->
  # Find which column is the one with the ID
  names = _.pluck columns, "name"
  index = _.indexOf(names, idName) + 1 # nth-child is 1-indexed

  highlightColumn tableWrapper, index


setHighlightOnSort = (tableWrapper) ->
  headers = $ "##{tableWrapper} th"
  headers.click (event) ->
    target = $ event.currentTarget
    # If this is the column that the table is currently sorted by
    if target.hasClass("ascending") or target.hasClass("descending")
      columnIndex = headers.index(target) + 1
      highlightColumn tableWrapper, columnIndex


setClearSortingOnSearch = (tableWrapper) ->
  clearHighlight = () ->
      $("##{tableWrapper} th.ascending").removeClass "ascending"
      $("##{tableWrapper} th.descending").removeClass "descending"

  $ "##{tableWrapper} input[type='search']"
    .keypress () -> clearHighlight()

  $ "##{tableWrapper} a.clear"
    .keypress () ->
      clearHighlight()
      $("##{tableWrapper} th .sorted-indicator").hide() # clear the caret


addSortedIndicator = (tableWrapper) ->
  selector = "##{tableWrapper} th"

  # Prepend it so it can float to the right
  $ selector
    .prepend "<div>"

  $ selector + " > div"
    .addClass "sorted-indicator"
    .html "<i class='fa fa-sort-amount-asc'></i>"



setSearchIcons = (tableWrapper) ->
  $ "##{tableWrapper} .form-search"
    .append "<i class='fa fa-search'></i>"  # Add the new search icon
        .find ".clear" # Find the default clear icon
        .html "<i class='fa fa-times'></i>" # Add the new clear icon
        # TODO make clear button responsive (stick to 5px from the left input corner)
        #.appendTo("##{tableWrapper} .form-search input[type='search']"); // Move it next to the input


setSearchSize = (tableWrapper) ->
  $ "##{tableWrapper} .form-search"
    .wrap '<section class="above-rows">'
    .wrap '<div class="row control-row">'
    .wrap '<div class="col-xs-10 search-cols">'


addColumnFiltering = (tableWrapper) ->
  $ '<div class="col-xs-1 filter-cols">'
    .html '<button class="btn btn-primary"><i class="fa fa-filter fa-lg"></i></button>'
    .insertAfter "##{tableWrapper} .search-cols"
  # TODO add the filters


setSearchEscClear = (tableWrapper) ->
  input = $ "##{tableWrapper} .form-search input"
  input.keypress (event) ->
    code = event.keyCode || event.which
    # On Escape press
    input.val('') if code is 27


addEntityForm = (tableWrapper, columnWidths, regexes) ->
  # Build the horizontal entry form
  # TODO get this from django forms
  form = $ '<form class="form-inline entry-form" action="">'
    .html """
          <input placeholder='Auto ID' disabled title="The ID is generated automatically">
          <input placeholder='Parcel'   validation-req validation-regex='locationIdentifier'>
          <input placeholder='Row'      validation-req validation-regex='locationIdentifier'>
          <input placeholder='Column'   validation-req validation-regex='locationIdentifier'>
          <input placeholder='Year'     validation-req validation-regex='year'>
          <input placeholder='Value'    validation-req validation-regex='currency'>
          <input placeholder='Receipt'  validation-req validation-regex='numberPerYear'>
          <br><br><br>
          <button type='submit' class='btn btn-success add-button'><i class='fa fa-plus fa-lg'>
          """
          # TODO remove br's and style it correctly!
  inputs = form.find "input"
  setRegexMessages inputs

  validationDelay = 400
  inputs
    # FIXME tooltips get shown/hidden only if you mouse over them very slowly
    .attr
      type: "text"
      "data-toggle": "tooltip"
      "data-placement": "top"
      container: "body"
    .addClass "form-control"
    .wrap "<div class='form-group'>"
    .typeWatch
      callback: validateInput
      wait: validationDelay
      captureLength: 1

  #addWidths form.find('input'), columnWidths, colType

  # Initially, the form is hidden
  #form.hide()

  # Setup the validation
  form.submit () ->
    checkInputs this

  # Insert the form
  $ '<div class="row entry-row">'
    .append form
    .insertAfter "##{tableWrapper} .control-row"

  slidingDuration = 100
  # Insert the display button
  $ '<div class="col-xs-1 add-cols">'
    .html '<button class="btn btn-default"><i class="fa fa-plus fa-lg">'
    .insertAfter "##{tableWrapper} .filter-cols"
    .click () ->
      if form.is(':visible')
        form.slideUp slidingDuration
      else
        form.slideDown slidingDuration





# Validation


class ValidationInfo
  constructor: (@regex, @message) ->


validationInfos =
  locationIdentifier: new ValidationInfo /^\d([Bb][Ii][Ss]|[A-Za-z])?$/,      "A digit followed by a letter or 'bis'" # TODO treat 2a as 2A
  year:               new ValidationInfo /(^['`]?\d{2}$)|(^\d{4}$)/,          "A year like 2015, 15 or '94" # TODO convert 09 to 2009 and 94 to 2004, warn (bootstrap styling) if year is absurd
  currency:           new ValidationInfo /^\d{1,6}$/,                         "A number up to 6 digits long" # TODO warn if value is at least three times as big than the others
  numberPerYear:      new ValidationInfo /^\d{1,3}\/((['`]?\d{2})|(\d{4}))$/, "A number up to 3 digits long, followed by / and then a year like 2015, 15 or '94" # TODO same as year conversion, autocomplete this to last + 1 of curr year? (and auto-select it on tab)


setRegexMessages = (inputs) ->
  for input in inputs
    $input = $ input
    regexName = $input.attr "validation-regex"

    if regexName?
      $input.attr title: validationInfos[regexName].message
      $input.tooltip()


validateInput = (arg) ->
  if typeof arg is "string"
    input = this
    value = arg
  else
    input = arg
    value = $(input).val()

  $input = $ input
  regexName = $input.attr "validation-regex"
  isRequired = $input.attr "validation-req"

  className = ""

  regexIsRelevant = true
  # If it is required but the value is empty
  if isRequired?
    if value is ""
      className = "has-error"
      regexIsRelevant = false
  else
    regexIsRelevant = false if value is ""

  # If there is a regex and the requiredness hasn't been violated
  if regexIsRelevant and regexName?
    regex = validationInfos[regexName].regex
    className = if regex.test value then "has-success" else "has-error"

  $input.parent()
    .removeClass "has-success has-error"
    .addClass className

  return className in ["", "has-success"]


checkInputs = (form) ->
  inputs = $(form).find "input"
  allValid = true

  for input in inputs
    if not validateInput input
      $(input).tooltip("show")
      allValid = false

  return allValid


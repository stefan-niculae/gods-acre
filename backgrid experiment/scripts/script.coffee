# External variables

tableWrapper = "example-table"
columnWidths = [1, 1, 1, 1, 2, 3, 3]





# Utils

sum = (arr) ->
  arr.reduce (prev, curr) -> prev + curr

translateShortYear = (year) ->
  YEAR_THRESHOLD = 50
  # Make sure it's a number
  year = +year

  # 15 => 2015
  if 0 <= year <= YEAR_THRESHOLD
    2000 + year
  # 94 => 1994
  else if YEAR_THRESHOLD < year < 100
    1900 + year
  # Year is already like 2015
  else
    year

currentYear = new Date().getFullYear()





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
    console.error "Fetching failed. Error response: #{response}."


# Bootstrap styling

bootstrapColumns = 12

addWidths = (elements, widths, colType) ->
  colType = "lg"
  for [elem, width] in _.zip elements, widths
    $(elem).addClass s.sprintf "col-%s-%d", colType, width

setColumnWidths = (tableWrapper, widths, colType) ->
  if sum(widths) != bootstrapColumns
    console.error "Total number of columns (#{sum widths}) differs from total number of bootstrap columns (#{bootstrapColumns})."

  # Prepend with a zero to account for the SelectAll column
  # and append a zero to account for the editing buttons
  adjustedWidths = [0].concat widths
  adjustedWidths.push 0

  headers = $ "#" +  tableWrapper + " th"
  # Subtract one for the SelectAll column and one for the editing buttons column
  if headers.length - 2 != widths.length
      console.error "The number of columns (#{widths.length}) differs from the number of headers (#{headers.length - 2})."

  addWidths headers, adjustedWidths, colType


repositionRow = (grid, oldIndex, newIndex) ->
  rows = grid.$el.find "tbody tr"
  n = rows.length

  if n is 0
    console.error "Grid is empty"
    return

  if Math.abs(oldIndex) >= n or Math.abs(newIndex) > n
    console.error "Index (old one, #{oldIndex} or new one, #{newIndex}) is larger than the number of rows (#{n})"
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
          <input placeholder='Auto ID' disabled data-hint="The ID is generated automatically">
          <input placeholder='Parcel'   validation-req validation-regex='locationIdentifier'>
          <input placeholder='Row'      validation-req validation-regex='locationIdentifier'>
          <input placeholder='Column'   validation-req validation-regex='locationIdentifier'>
          <input placeholder='Year'     validation-req validation-regex='year'                validation-warn='closeYear'>
          <input placeholder='Value'    validation-req validation-regex='currency'>
          <input placeholder='Receipt'  validation-req validation-regex='numberPerYear'>
          <br><br><br>
          <button type='submit' class='btn btn-success add-button'><i class='fa fa-plus fa-lg'>
          """
          # TODO remove br's and style it correctly!
  inputs = form.find "input"
  # Initially, show the regex validation message

  validationDelay = 400
  inputs
    .attr type: "text"
    .addClass "form-control"
    .wrap "<div class='form-group'>"
    .wrap "<span class='hint--top hint--rounded'>"
    .typeWatch
      callback: validateInput
      wait: validationDelay
      captureLength: 1
  setRegexMessages inputs

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


class ValidationRegex
  constructor: (@regex, @message) ->


validationRegexes =
  locationIdentifier: new ValidationRegex /^\d([Bb][Ii][Ss]|[A-Za-z])?$/,      "A digit followed by a letter or 'bis'" # TODO treat 2a as 2A
  year:               new ValidationRegex /(^['`]?\d{2}$)|(^\d{4}$)/,          "A year like 2015, 15 or '94" # TODO convert 09 to 2009 and 94 to 2004, warn (bootstrap styling) if year is absurd
  currency:           new ValidationRegex /^\d{1,6}$/,                         "A number up to 6 digits long" # TODO warn if value is at least three times as big than the others
  numberPerYear:      new ValidationRegex /^\d{1,3}\/((['`]?\d{2})|(\d{4}))$/, "A number up to 3 digits long, followed by a slash / and then a year, like 2015, 15 or '94" # TODO same as year conversion, autocomplete this to last + 1 of curr year? (and auto-select it on tab)


class ValidationWarning
  constructor: (@filter, @message) ->


closeYearFilter = (year) ->
  # Remove the apostrophe
  year = year[1..] if year[0] in ["'", "`"]
  # Translate the year if necessary
  year = translateShortYear year
  console.log "entered year is #{year}"
  return Math.abs(year - currentYear) > 100

validationWarnings =
  closeYear: new ValidationWarning closeYearFilter, "Entered year is more than 100 years apart from today"


class InputState
  constructor: (@bootstrapClass, @hintClass) ->


INPUT_STATES =
  NEUTRAL:  new InputState "", ""
  ERROR:    new InputState "has-error", "hint--error"
  WARNING:  new InputState "has-warning", "hint--warning"
  SUCCESS:  new InputState "has-success", "hint--success"

bootstrapStateClasses = _.pluck(INPUT_STATES, "bootstrapClass").join(' ')
hintStateClasses      = _.pluck(INPUT_STATES, "hintClass")     .join(' ')


setRegexMessages = (inputs) ->
  for input in inputs
    $input = $ input
    regexName = $input.attr "validation-regex"

    if regexName?
      info = validationRegexes[regexName]
      $input.parent().attr "data-hint": info.message unless info is undefined


validateInput = (arg) ->
  # Two ways of calling this: by string and with the input as 'this'...
  if typeof arg is "string"
    input = this
    value = arg
  # ... or directly by the input element
  else
    input = arg
    value = $(input).val()

  $input = $ input
  regexName   = $input.attr "validation-regex"
  isRequired  = $input.attr "validation-req"
  warningName = $input.attr "validation-warn"


  # TODO merge passes (req, regex, warn) into one (but keep it legible)
  passesRequiredness = () ->
    if not isRequired?
      return [true, "Ok!", INPUT_STATES.NEUTRAL]

    if value isnt ""
      # Is required and something is entered
      return [true, "Ok!", INPUT_STATES.NEUTRAL]
    else
      # No need to say what is required as the placeholder shows that...
      # ... and the placeholder is visible because there is nothing entered
      return [false, "Required", INPUT_STATES.ERROR]


  passesRegex = () ->
    if not regexName?
      return [true, "Ok!", INPUT_STATES.NEUTRAL]

    {regex, message} = validationRegexes[regexName]
    if regex is undefined
      console.error "#{regexName} was not found in the validationRegexes dictionary."
      return [true, "Ok!", INPUT_STATES.NEUTRAL]

    if regex.test value
      return [true, "Ok!", INPUT_STATES.SUCCESS]
    else
      return [false, message, INPUT_STATES.ERROR]


  passesWarning = () ->
    if not warningName?
      return [true, "Ok!", INPUT_STATES.NEUTRAL]

    {filter, message} = validationWarnings[warningName]
    if filter is undefined
      console.error "#{warningName} was not found in the validationWarnings dictionary."
      return [true, "Ok!", INPUT_STATES.NEUTRAL]

    # If it triggers a warning
    if filter value
      return [false, message, INPUT_STATES.WARNING]
    else
      return [true, "Ok!", INPUT_STATES.NEUTRAL]

  validationResults = () ->
    # We test things in this order: requiredess, regex and warnings
    for [hasPassed, message, state] in [passesRequiredness(), passesRegex(), passesWarning()]
      if not hasPassed
        return [message, state]
    return ["Ok!", INPUT_STATES.SUCCESS]


  [message, state] = validationResults()

  # Setting the bootstrap class
  $input.parent().parent()
    .removeClass "#{bootstrapStateClasses}"
    .addClass state.bootstrapClass

  # Setting the hint class
  $input.parent()
    .attr "data-hint": message
    .removeClass "#{hintStateClasses}"
    .addClass state.hintClass

  return state in [INPUT_STATES.NEUTRAL, INPUT_STATES.SUCCESS]



checkInputs = (form) ->
  showTooltip = (elem) ->
    elem
    # Force showing the tooltip
      .addClass("hint--always")
      # But return to normal behaviour once hovered over
      .hover (event) ->
        $(event.currentTarget)
          .removeClass "hint--always"


  # Act on all inputs except the ID one (which is automatically generated), assumed to be first
  inputs = $(form).find("input")[1..]
  allValid = true

  for input in inputs
    if not validateInput input
      showTooltip $(input).parent()
      allValid = false

  return allValid


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
  url: 'encashments.json'

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
    this.$el.focus().val('').val(val)

alignedIntegerCell = Backgrid.IntegerCell.extend
  className: 'aligned-integer-cell'
  editor: cursorAtEndEditor

stringCell = Backgrid.StringCell.extend
  editor: cursorAtEndEditor

columns = [
  {
    name: '' # Required (but we don't need one on a select all column)
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
        orderSeparator: '' # No thousands separator for the ID
        className: 'id-cell'
      )
    sortType: 'toggle'
    direction: 'ascending' # Data should come sorted by ID
  }
  {
    name: 'parcel'
    label: 'P'
    cell: stringCell
    sortType: 'toggle'
  }
  {
    name: 'row'
    label: 'R'
    cell: stringCell
    sortType: 'toggle'
  }
  {
    name: 'column'
    label: 'C'
    cell: stringCell
    sortType: 'toggle'
  }
  {
    name: 'year'
    label: 'Year'
    cell: alignedIntegerCell.extend(
        orderSeparator: '' # No thousands separator for the year
        className: 'year-cell'
      )
    sortType: 'toggle'
  }
  {
    name: 'value'
    label: 'Value'
    cell: alignedIntegerCell
    sortType: 'toggle'
  }
  {
    name: 'receipt'
    label: 'Receipt'
    cell: stringCell
    sortType: 'toggle'
  }
  {
    name: 'editing-buttons'
    label: ''
    formatter: _.extend {}, Backgrid.CellFormatter.prototype,
      fromRaw: () ->
        "<button type='button' class='btn btn-info duplicate'><i class='fa fa-files-o'></i></button>" +
        "<button type='button' class='btn btn-danger  delete'><i class='fa fa-trash-o'></i></button>"
    cell: Backgrid.HtmlCell.extend(
      className: 'editing-buttons-cell'
    )
    sortable: false
    editable: false
  }
]



# Initialize a new Grid instance
grid = new Backgrid.Grid
  columns: columns
  collection: encashments
  className: 'backgrid table table-striped table-bordered table-condense table-hover'
  emptyText: 'No data' # TODO better message for empty data (centered, and no highlight id header)

# Render grid and attack to DOM
$tableWrapper = $ '#' + tableWrapper
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
  placeholder: 'Search' #TR
  # The model fields to search for matches
  fields: ['id', 'parcel', 'row', 'column', 'year', 'value', 'receipt']
  # How long to wait after typing has stopped before searching can
  wait: 150

$tableWrapper.prepend clientSideFilter.render().el



# Fetch from the url
encashments.fetch
  reset: true
  success: () ->
    # Insert blank row for adding new entries
    # TODO hide the -1 tricks, make it work properly
    insertBlankRow grid

    setColumnWidths tableWrapper, columnWidths, colType

    setInitialSortedHighlight tableWrapper, columns, 'id'
    setHighlightOnSort tableWrapper
    addSortedIndicator tableWrapper

    setSearchIcons tableWrapper
    setSearchSize tableWrapper
    setSearchEscClear tableWrapper

    addColumnFiltering tableWrapper

  error: (collection, response) ->
    printError 'Fetching failed. Error response: %s.', response


# Bootstrap styling

bootstrapColumns = 12
colType = 'lg'

setColumnWidths = (tableWrapper, widths, colType) ->
  if sum(widths) != bootstrapColumns
    msg = 'Total number of columns (%d) differs from total number of bootstrap columns (%d).'
    printError msg, sum widths, bootstrapColumns

  # Prepend with a zero to account for the SelectAll column
  # and append a zero to account for the editing buttons
  adjustedWidths = [0]
  adjustedWidths.push w for w in widths
  adjustedWidths.push 0

  headers = $ '#' +  tableWrapper + ' th'
  # Subtract one for the SelectAll column and one for the editing buttons column
  if headers.length - 2 != widths.length
      msg = 'The number of columns (%d) differs from the number of headers (%d).'
      printError msg, widths.length, headers.length - 2

  for headerWidthPair in _.zip headers, adjustedWidths
    header = $ headerWidthPair[0]
    width = headerWidthPair[1]
    header.addClass s.sprintf 'col-%s-%d', colType, width


insertBlankRow = (grid) ->
  # TODO make this always be first (and dissapear on searching)
  blankRow =
    id: -1
    parcel: ''
    row: ''
    column: ''
    year: -1
    value: -1
    receipt: ''

  # Insert the 'blank' line at the top
  grid.insertRow blankRow
  row = repositionRow grid, -1, 0
  row.addClass 'blank-row'

  # Ignore the SelectAll and editable buttons cells
  # assumes they are on the first and last positions
  row.find 'td'
    .slice 1, -1
    # Make all cells text empty except the id one
    .each (index, elem) ->
      $elem = $ elem
      $elem.text if $elem.hasClass 'id-cell' then '-' else ''


repositionRow = (grid, oldIndex, newIndex) ->
  # TODO error cases for index out of bounds/empty grid
  rows = grid.$el.find 'tbody tr'
  n = rows.length

  # -1 becomes n - 1
  oldIndex = n + oldIndex if oldIndex < 0
  newIndex = n + newIndex if newIndex < 0

  toMove = rows.eq oldIndex
  aboveWhat = rows.eq newIndex
  toMove.insertBefore aboveWhat


highlightColumn = (tableWrapper, columnIndex) ->
  # FIXME
  $ '#' + tableWrapper + ' td:nth-child(' + columnIndex + ')'
    .add '#' + tableWrapper + ' th:nth-child(' + columnIndex + ')'
    .toggleClass 'sorted-col'


setInitialSortedHighlight = (tableWrapper, columns, idName) ->
  # FIXME does nothing now
  # Find which column is the one with the ID
  names = _.pluck columns, 'name'
  index = _.indexOf names, idName + 1 # nth-child is 1-indexed

  highlightColumn tableWrapper, index


setHighlightOnSort = (tableWrapper) ->
  headers = $ '#' + tableWrapper + ' th'
  headers.click (event) ->
    target = $ event.currentTarget
    # If this is the column that the table is currently sorted by
    if target.hasClass 'ascending' || target.hasClass 'descending'
      columnIndex = headers.index(target) + 1
      highlightColumn tableWrapper, columnIndex


clearHeaderHighlights = (tableWrapper) ->
  # Clear only the header, as the rows reset automatically on search
  $ '#' + tableWrapper + ' th.sorted-col'
    .removeClass 'sorted-col'


setHighlightClearOnSearch = (tableWrapper) ->
  $ '#' + tableWrapper + ' input[type="search"]'
    .keyPress () ->
      clearHeaderHighlights tableWrapper



addSortedIndicator = (tableWrapper) ->
  selector = '#' + tableWrapper + ' th'

  # Prepend it so it can float to the right
  $ selector
    .prepend '<div>'

  $ selector + ' > div'
    .addClass 'sorted-indicator'
    .html "<i class='fa fa-sort-amount-asc'></i>"


setSearchIcons = (tableWrapper) ->
  $ '#' + tableWrapper + ' .form-search'
    .append "<i class='fa fa-search'></i>"  # Add the new search icon
        .find '.clear' # Find the default clear icon
        .html "<i class='fa fa-times'></i>" # Add the new clear icon
        # TODO make clear button responsive (stick to 5px from the left input corner)
        #.appendTo("#" + tableWrapper + " .form-search input[type='search']"); // Move it next to the input


setSearchSize = (tableWrapper) ->
  $ '#' + tableWrapper + ' .form-search'
    .wrap "<div class='row search-and-filter-row'>"
    .wrap "<div class='col-xs-10 search-cols'>"


addColumnFiltering = (tableWrapper) ->
  $ "<div class='col-xs-offset-1 col-xs-1 filter-cols'>"
    .html "<button type='button' class='btn btn-primary'><i class='fa fa-filter fa-lg'></i></button>"
    .insertAfter '#' + tableWrapper + ' .search-cols'


setSearchEscClear = (tableWrapper) ->
  input = $ '#' + tableWrapper + ' .form-search input'
  input.keypress (event) ->
    code = event.keyCode || event.which
    # On Escape press
    input.val('') if code == 27


addRowButtons = (tableWrapper) ->
  # This is not the best way to do this
  $ '#' + tableWrapper + ' tr .editing-buttons-cell'
    # Add the duplicate and the delete buttons
    .append "<button type='button' class='btn btn-info duplicate'><i class='fa fa-files-o'></i></button>"
    .append "<button type='button' class='btn btn-danger delete'><i class='fa fa-trash-o'></i></button>"

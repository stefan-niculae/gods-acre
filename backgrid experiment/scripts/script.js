// External variables

var tableWrapper = "example-table";
var columnWidths = [1, 1, 1, 1, 2, 3, 3];


// Utils

var sum = function (array) {
    return array.reduce(function (pv, cv) { return pv + cv; }, 0);
};

//var printError = function (format, ...args) {
//    var message = s.sprintf(format, ...args);
//    console.error(message);
//};





// Backgrid config & fetch

var Encashment = Backbone.Model.extend({});
//var Encashments = Backbone.PageableCollection.extend({
var Encashments = Backbone.Collection.extend({
    model: Encashment,
    url: "encashments.json"
    
    // TODO pagination
//    // Initial pagination states
//    state: {
//        pageSize: 10,
//        sortKey: "id",
//        order: 1
//    },
});
var encashments = new Encashments();

var cursorAtEndEditor = Backgrid.InputCellEditor.extend({
    postRender: function() {
        var val = this.$el.val();
        this.$el.focus().val('').val(val);
        return this;
    }
});

var alignedIntegerCell = Backgrid.IntegerCell.extend({
    className: "aligned-integer-cell",
    editor: cursorAtEndEditor
});

var stringCell = Backgrid.StringCell.extend({
    editor: cursorAtEndEditor
});

var columns = [
    // SelectAll extension
    {
        name: "", // Required (but we don't need one on a select all column)
        cell: "select-row", // Selecting individual rows
        headerCell: "select-all", // Select all the rows on a page
        editable: false,
        sortable: false
    },
    {
        name: "id", // The key of the model attribute
        label: "#", // The name to display in the header
        editable: false, // ID isn't editable
        cell: alignedIntegerCell.extend({
            orderSeparator: '', // No thousands separator for the ID
            className: "id-cell"
        }),
        sortType: "toggle",
        direction: "ascending" // Data should come sorted by ID
    },
    {
        name: "parcel",
        label: "P",
        cell: stringCell,
        sortType: "toggle"
    },
    {
        name: "row",
        label: "R",
        cell: stringCell,
        sortType: "toggle"
    },
    {
        name: "column",
        label: "C",
        cell: stringCell,
        sortType: "toggle"
    },
    {
        name: "year",
        label: "Year",
        cell: alignedIntegerCell.extend({
            orderSeparator: '' // No thousands separator for the year
        }),
        sortType: "toggle"
    },
    {
        name: "value",
        label: "Value",
        cell: alignedIntegerCell,
        sortType: "toggle"
    },
    {
        name: "receipt",
        label: "Receipt",
        cell: stringCell,
        sortType: "toggle"
    },
    {
        name: "editing-buttons",
        label: "",
        formatter: _.extend({}, Backgrid.CellFormatter.prototype, {
            fromRaw: function () {
                return "<button type='button' class='btn btn-info duplicate'><i class='fa fa-files-o'></i></button>" +
                       "<button type='button' class='btn btn-danger  delete'><i class='fa fa-trash-o'></i></button>";
            }
        }),
        cell: Backgrid.HtmlCell.extend({
            className: "editing-buttons-cell"
        }),
        sortable: false,
        editable: false
    }
];

// Initialize a new Grid instance
var grid = new Backgrid.Grid({
    columns: columns,
    collection: encashments,
    className: "backgrid table table-striped table-bordered table-condense table-hover",
    emptyText: "No data" // TODO better message for empty data (centered, and no highlight id header)
});

// Render grid and attach to DOM
$tableWrapper = $("#" + tableWrapper);
$tableWrapper.append(grid.render().el);

// TODO pagination
//var paginator = new Backgrid.Extension.Paginator({
//    // If you anticipate a large number of pages, you can adjust
//    // the number of page handles to show. The sliding window
//    // will automatically show the next set of page handles when
//    // you click next at the end of a window.
//    windowSize: 20, // Default is 10
//
//    // Used to multiple windowSize to yield a number of pages to slide,
//    // in the case the number is 5
//    slideScale: 0.25, // Default is 0.5
//
//    // Whether sorting should go back to the first page
//    goBackFirstOnSort: true, // Default is true
//
//    collection: encashments
//});
//
//$tableWrapper.append(paginator.render().el);

// case-insensitive regex search on the client side 
// by OR-ing the keywords in the search box
var clientSideFilter = new Backgrid.Extension.ClientSideFilter({
  collection: encashments,
  placeholder: "Search",
  // The model fields to search for matches
  fields: ['id', 'parcel', 'row', 'column', 'year', 'value', 'receipt'],
  // How long to wait after typing has stopped before searching can start
  wait: 150
});

$tableWrapper.prepend(clientSideFilter.render().el);


// Fetch from the url
encashments.fetch({
    reset: true,
    success: function() {
        // Insert blank row for adding new entries
        insertBlankRow(grid);
        
        setColumnWidths(tableWrapper, columnWidths, colType);
        
        setInitialSortedHighlight(tableWrapper, columns, "id");
        setHighlightOnSort(tableWrapper);
        addSortedIndicator(tableWrapper);
        
        setSearchIcons(tableWrapper);
        setSearchSize(tableWrapper);
        setSearchEscClear(tableWrapper);
        
        addColumnFiltering(tableWrapper);  
    },
    error: function(collection, response) {
        console.error("Fetching failed. Error response: " + response + ".");  
    }
});



// Bootstrap styling

var bootstrapColumns = 12;
var colType = "lg";


function setColumnWidths(tableWrapper, widths, colType) {
    if (sum(widths) != bootstrapColumns)
        printError("Total number of columns (%d) differs from total number of bootstrap columns (%d).",
            sum(widths),
            bootstrapColumns);
    
    // Prepend with a zero to account for the SelectAll column
    // ... and append a zero to account for the editing buttons
    var adjustedWidths = [0];
    for (var i = 0, len = widths.length; i < len; i++) {
        var w = widths[i];
        adjustedWidths.push(w);
    }
    adjustedWidths.push(0);
    
    var headers = $("#" + tableWrapper + " th");
    if (headers.length - 2 != widths.length)
        printError("The number of columns (%d) differs from the number of headers (%d).",
            widths.length,
            headers.length - 2);

    var ref = _.zip(headers, adjustedWidths);
    for (var j = 0, len1 = ref.length; j < len1; j++) {
      var headerWidthPair = ref[j];
      var header = $(headerWidthPair[0]);
      var width = headerWidthPair[1];
      header.addClass(s.sprintf('col-%s-%d', colType, width));
    }
}


function insertBlankRow(grid) {
    var blankRow = {
        "id": -1,
        "parcel": "",
        "row": "",
        "column": "",
        "year": -1,
        "value": -1,
        "receipt": ""
    };
    
    // Insert the "blank" line at the top
    grid.insertRow(blankRow);
    var row = repositionRow(grid, -1, 0);
    row.addClass("blank-row");
    
    // Ignore the selectAll and editable buttons cells
    // assumes they are on the first and last position
    row.find("td")
        .slice(1, -1)
        // Make all cells text empty except for the id one
        .each(function (index, elem) {
            $elem = $(elem);
            if ($elem.hasClass("id-cell"))
                $elem.text("-");
            else
                $elem.text("");
        });
    
}
        
function repositionRow(grid, oldIndex, newIndex) {
    // TODO error cases for index out of bounds/empty grid
    var rows = grid.$el.find("tbody tr");
    if (oldIndex < 0)
        oldIndex = rows.length - -oldIndex;
    if (newIndex < 0)
        newIndex = rows.length - -newIndex;

    var toMove = rows.eq(oldIndex);
    var aboveWhat = rows.eq(newIndex);
    toMove.insertBefore(aboveWhat);
    
    return toMove;
}


// TODO reset column color after search
function highlightColumn(columnIndex) {
    $("#" + tableWrapper + " td:nth-child(" + columnIndex + ")")
        .toggleClass("sorted-col");
}

function setInitialSortedHighlight(tableWrapper, columns, idName) {
    // Finding which column is the one with the ID
    var names = _.pluck(columns, "name");
    var index = _.indexOf(names, idName) + 1; // nth child is one-indexed
    
    highlightColumn(index);
}

function setHighlightOnSort(tableWrapper) {
    var headers = $("#" + tableWrapper + " th");
    headers.click(function(event) {
        var target = $(event.currentTarget);
        // If this is the column that the table is currently sorted by
        if (target.hasClass("ascending") || target.hasClass("descending")) {
            var columnIndex = headers.index(target) + 1; // jQuery's nth child is one-indexed
            highlightColumn(columnIndex);
        }
    });
}

function addSortedIndicator(tableWrapper) {
    var selector = "#" + tableWrapper + " th";
    // Prepend it so it can float to the right
    $(selector).prepend("<div>");
    var indicators = $(selector + " > div");
    
    // Add the indicator
    indicators
        .addClass("sorted-indicator")
        .html("<i class='fa fa-sort-amount-asc'></i>");   
}


function setSearchIcons(tableWrapper) {
    $("#" + tableWrapper + " .form-search")
        .append("<i class='fa fa-search'></i>") // Add the new search icon
        .find(".clear") // Find the default clear icon
        .html("<i class='fa fa-times'></i>") // Add the new clear icon
    // TODO make clear button responsive (stick to 5px from the left input corner)
//        .appendTo("#" + tableWrapper + " .form-search input[type='search']"); // Move it next to the input
}

function setSearchSize(tableWrapper) {
    $("#" + tableWrapper + " .form-search")
        .wrap("<div class='row search-and-filter-row'>")
        .wrap("<div class='col-xs-10 search-cols'>");
}

function addColumnFiltering(tableWrapper) {
    $("<div class='col-xs-offset-1 col-xs-1 filter-cols'>")
        .html("<button type='button' class='btn btn-primary'><i class='fa fa-filter fa-lg'></i></button>")
        .insertAfter("#" + tableWrapper + " .search-cols");
}

function setSearchEscClear(tableWrapper) {
    var input = $("#" + tableWrapper + " .form-search input");
    input.keypress(
        function (event) {
            var code = event.keyCode || event.which;
            // On Escape press
            if (code === 27)
                input.val("");
        }
    );
}


function addRowButtons(tableWrapper) {
    // This is not the best way to do this
    $("#" + tableWrapper + " tr .editing-buttons-cell")
        // Add the duplicate and delete buttons
        .append("<button type='button' class='btn btn-info duplicate'><i class='fa fa-files-o'></i></button>")
        .append("<button type='button' class='btn btn-danger delete'><i class='fa fa-trash-o'></i></button>");
}

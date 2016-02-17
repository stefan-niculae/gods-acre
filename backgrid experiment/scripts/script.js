// Generated by CoffeeScript 1.10.0
(function() {
  var $tableWrapper, Encashment, Encashments, INPUT_STATES, InputState, ValidationRegex, ValidationWarning, addEntityFormTriggers, addSortedIndicator, addWidths, alignedIntegerCell, bootstrapColumns, bootstrapStateClasses, checkInputs, clientSideFilter, closeYearFilter, columnWidths, columns, currentYear, cursorAtEndEditor, encashments, grid, highlightColumn, hintStateClasses, repositionRow, repositionSearch, setClearSortingOnSearch, setColumnWidths, setHighlightOnSort, setInitialSortedHighlight, setRegexMessages, setSearchEscClear, setSearchIcons, stringCell, sum, tableWrapper, translateShortYear, validateInput, validationRegexes, validationWarnings;

  tableWrapper = "example-table";

  columnWidths = [1, 1, 1, 1, 2, 3, 3];

  sum = function(arr) {
    return arr.reduce(function(prev, curr) {
      return prev + curr;
    });
  };

  translateShortYear = function(year) {
    var YEAR_THRESHOLD;
    YEAR_THRESHOLD = 50;
    year = +year;
    if ((0 <= year && year <= YEAR_THRESHOLD)) {
      return 2000 + year;
    } else if ((YEAR_THRESHOLD < year && year < 100)) {
      return 1900 + year;
    } else {
      return year;
    }
  };

  currentYear = new Date().getFullYear();

  Encashment = Backbone.Model.extend({});

  Encashments = Backbone.Collection.extend({
    model: Encashment,
    url: "encashments.json"
  });

  encashments = new Encashments();

  cursorAtEndEditor = Backgrid.InputCellEditor.extend({
    postRender: function() {
      var val;
      val = this.$el.val();
      return this.$el.focus().val("").val(val);
    }
  });

  alignedIntegerCell = Backgrid.IntegerCell.extend({
    className: "aligned-integer-cell",
    editor: cursorAtEndEditor
  });

  stringCell = Backgrid.StringCell.extend({
    editor: cursorAtEndEditor
  });

  columns = [
    {
      name: "",
      cell: 'select-row',
      headerCell: 'select-all',
      editable: false,
      sortable: false
    }, {
      name: 'id',
      label: '#',
      editable: false,
      cell: alignedIntegerCell.extend({
        orderSeparator: "",
        className: "id-cell"
      }),
      sortType: "toggle",
      direction: "ascending"
    }, {
      name: "parcel",
      label: "P",
      cell: stringCell,
      sortType: "toggle"
    }, {
      name: "row",
      label: "R",
      cell: stringCell,
      sortType: "toggle"
    }, {
      name: "column",
      label: "C",
      cell: stringCell,
      sortType: "toggle"
    }, {
      name: "year",
      label: "Year",
      cell: alignedIntegerCell.extend({
        orderSeparator: "",
        className: "year-cell"
      }),
      sortType: "toggle"
    }, {
      name: "value",
      label: "Value",
      cell: alignedIntegerCell,
      sortType: "toggle"
    }, {
      name: "receipt",
      label: "Receipt",
      cell: stringCell,
      sortType: "toggle"
    }, {
      name: "editing-buttons",
      label: "",
      formatter: _.extend({}, Backgrid.CellFormatter.prototype, {
        fromRaw: function() {
          return "<button class=\"btn btn-info duplicate\"><i class=\"fa fa-files-o\"></i></button>\n<button class=\"btn btn-danger  delete\"><i class=\"fa fa-trash-o\"></i></button>";
        }
      }),
      cell: Backgrid.HtmlCell.extend({
        className: "editing-buttons-cell"
      }),
      sortable: false,
      editable: false
    }
  ];

  grid = new Backgrid.Grid({
    columns: columns,
    collection: encashments,
    className: "backgrid table table-striped table-bordered table-condense table-hover",
    emptyText: "No data"
  });

  $tableWrapper = $("#" + tableWrapper);

  $tableWrapper.append(grid.render().el);

  clientSideFilter = new Backgrid.Extension.ClientSideFilter({
    collection: encashments,
    placeholder: "Search",
    fields: ["id", "parcel", "row", "column", "year", "value", "receipt"],
    wait: 200
  });

  $tableWrapper.prepend(clientSideFilter.render().el);

  encashments.fetch({
    reset: true,
    success: function() {
      setColumnWidths(tableWrapper, columnWidths);
      setInitialSortedHighlight(tableWrapper, columns, "id");
      setHighlightOnSort(tableWrapper);
      setClearSortingOnSearch(tableWrapper);
      addSortedIndicator(tableWrapper);
      setSearchIcons(tableWrapper);
      repositionSearch(tableWrapper);
      setSearchEscClear(tableWrapper);
      return addEntityFormTriggers(tableWrapper, columnWidths);
    },
    error: function(collection, response) {
      return console.error("Fetching failed. Error response: " + response + ".");
    }
  });

  bootstrapColumns = 12;

  addWidths = function(elements, widths, colType) {
    var elem, i, len, ref, ref1, results, width;
    if (colType == null) {
      colType = "lg";
    }
    ref = _.zip(elements, widths);
    results = [];
    for (i = 0, len = ref.length; i < len; i++) {
      ref1 = ref[i], elem = ref1[0], width = ref1[1];
      results.push($(elem).addClass(s.sprintf("col-%s-%d", colType, width)));
    }
    return results;
  };

  setColumnWidths = function(tableWrapper, widths, colType) {
    var adjustedWidths, headers;
    if (sum(widths) !== bootstrapColumns) {
      console.error("Total number of columns (" + (sum(widths)) + ") differs from total number of bootstrap columns (" + bootstrapColumns + ").");
    }
    adjustedWidths = [0].concat(widths);
    adjustedWidths.push(0);
    headers = $("#" + tableWrapper + " th");
    if (headers.length - 2 !== widths.length) {
      console.error("The number of columns (" + widths.length + ") differs from the number of headers (" + (headers.length - 2) + ").");
    }
    return addWidths(headers, adjustedWidths, colType);
  };

  repositionRow = function(grid, oldIndex, newIndex) {
    var aboveWhat, n, rows, toMove;
    rows = grid.$el.find("tbody tr");
    n = rows.length;
    if (n === 0) {
      console.error("Grid is empty");
      return;
    }
    if (Math.abs(oldIndex) >= n || Math.abs(newIndex) > n) {
      console.error("Index (old one, " + oldIndex + " or new one, " + newIndex + ") is larger than the number of rows (" + n + ")");
      return;
    }
    if (oldIndex < 0) {
      oldIndex = n + oldIndex;
    }
    if (newIndex < 0) {
      newIndex = n + newIndex;
    }
    toMove = rows.eq(oldIndex);
    aboveWhat = rows.eq(newIndex);
    return toMove.insertBefore(aboveWhat);
  };

  highlightColumn = function(tableWrapper, columnIndex) {
    return $("#" + tableWrapper + " td:nth-child(" + columnIndex + ")").addClass("sorted-col");
  };

  setInitialSortedHighlight = function(tableWrapper, columns, idName) {
    var index, names;
    names = _.pluck(columns, "name");
    index = _.indexOf(names, idName) + 1;
    return highlightColumn(tableWrapper, index);
  };

  setHighlightOnSort = function(tableWrapper) {
    var headers;
    headers = $("#" + tableWrapper + " th");
    return headers.click(function(event) {
      var columnIndex, target;
      target = $(event.currentTarget);
      if (target.hasClass("ascending") || target.hasClass("descending")) {
        columnIndex = headers.index(target) + 1;
        return highlightColumn(tableWrapper, columnIndex);
      }
    });
  };

  setClearSortingOnSearch = function(tableWrapper) {
    var clearHighlight;
    clearHighlight = function() {
      $("#" + tableWrapper + " th.ascending").removeClass("ascending");
      return $("#" + tableWrapper + " th.descending").removeClass("descending");
    };
    $("#" + tableWrapper + " input[type='search']").keypress(function() {
      return clearHighlight();
    });
    return $("#" + tableWrapper + " a.clear").keypress(function() {
      clearHighlight();
      return $("#" + tableWrapper + " th .sorted-indicator").hide();
    });
  };

  addSortedIndicator = function(tableWrapper) {
    var selector;
    selector = "#" + tableWrapper + " th";
    $(selector).prepend("<div>");
    return $(selector + " > div").addClass("sorted-indicator").html("<i class='fa fa-sort-amount-asc'></i>");
  };

  setSearchIcons = function(tableWrapper) {
    return $("#" + tableWrapper + " .form-search").append("<i class='fa fa-search'></i>").find(".clear").html("<i class='fa fa-times'></i>");
  };

  repositionSearch = function(tableWrapper) {
    $(".control-row").prepend('<div class="col-xs-10 search-cols">');
    return $(".search-cols").prepend($("#" + tableWrapper + " .form-search"));
  };

  setSearchEscClear = function(tableWrapper) {
    var input;
    input = $("#" + tableWrapper + " .form-search input");
    return input.keypress(function(event) {
      var code;
      code = event.keyCode || event.which;
      if (code === 27) {
        return input.val('');
      }
    });
  };

  addEntityFormTriggers = function(tableWrapper, columnWidths, regexes) {
    var form, inputs, slidingDuration, validationDelay;
    form = $("#" + tableWrapper + " .entry-form");
    inputs = form.find("input");
    validationDelay = 400;
    inputs.attr({
      type: "text"
    }).addClass("form-control").wrap("<div class='form-group'>").wrap("<span class='hint--top hint--rounded'>").typeWatch({
      callback: validateInput,
      wait: validationDelay,
      captureLength: 1
    });
    setRegexMessages(inputs);
    form.submit(function() {
      return checkInputs(this);
    });
    slidingDuration = 100;
    return form.find('.add-cols button').click(function() {
      if (form.is(':visible')) {
        return form.slideUp(slidingDuration);
      } else {
        return form.slideDown(slidingDuration);
      }
    });
  };

  ValidationRegex = (function() {
    function ValidationRegex(regex1, message1) {
      this.regex = regex1;
      this.message = message1;
    }

    return ValidationRegex;

  })();

  validationRegexes = {
    locationIdentifier: new ValidationRegex(/^\d([Bb][Ii][Ss]|[A-Za-z])?$/, "A digit followed by a letter or 'bis'"),
    year: new ValidationRegex(/(^['`]?\d{2}$)|(^\d{4}$)/, "A year like 2015, 15 or '15"),
    currency: new ValidationRegex(/^\d{1,6}$/, "A number up to 6 digits long"),
    numberPerYear: new ValidationRegex(/^\d{1,3}\/((['`]?\d{2})|(\d{4}))$/, "A number up to 3 digits long, followed by a slash / and then a year, like 2015, 15 or '15")
  };

  ValidationWarning = (function() {
    function ValidationWarning(filter1, message1) {
      this.filter = filter1;
      this.message = message1;
    }

    return ValidationWarning;

  })();

  closeYearFilter = function(year) {
    var ref;
    if ((ref = year[0]) === "'" || ref === "`") {
      year = year.slice(1);
    }
    year = translateShortYear(year);
    console.log("entered year is " + year);
    return Math.abs(year - currentYear) > 100;
  };

  validationWarnings = {
    closeYear: new ValidationWarning(closeYearFilter, "Entered year is more than 100 years apart from today")
  };

  InputState = (function() {
    function InputState(bootstrapClass, hintClass) {
      this.bootstrapClass = bootstrapClass;
      this.hintClass = hintClass;
    }

    return InputState;

  })();

  INPUT_STATES = {
    NEUTRAL: new InputState("", ""),
    ERROR: new InputState("has-error", "hint--error"),
    WARNING: new InputState("has-warning", "hint--warning"),
    SUCCESS: new InputState("has-success", "hint--success")
  };

  bootstrapStateClasses = _.pluck(INPUT_STATES, "bootstrapClass").join(' ');

  hintStateClasses = _.pluck(INPUT_STATES, "hintClass").join(' ');

  setRegexMessages = function(inputs) {
    var $input, i, info, input, len, regexName, results;
    results = [];
    for (i = 0, len = inputs.length; i < len; i++) {
      input = inputs[i];
      $input = $(input);
      regexName = $input.attr("validation-regex");
      if (regexName != null) {
        info = validationRegexes[regexName];
        if (info !== void 0) {
          results.push($input.parent().attr({
            "data-hint": info.message
          }));
        } else {
          results.push(void 0);
        }
      } else {
        results.push(void 0);
      }
    }
    return results;
  };

  validateInput = function(arg) {
    var $input, input, isRequired, message, passesRegex, passesRequiredness, passesWarning, ref, regexName, state, validationResults, value, warningName;
    if (typeof arg === "string") {
      input = this;
      value = arg;
    } else {
      input = arg;
      value = $(input).val();
    }
    $input = $(input);
    regexName = $input.attr("validation-regex");
    isRequired = $input.attr("validation-req");
    warningName = $input.attr("validation-warn");
    passesRequiredness = function() {
      if (isRequired == null) {
        return [true, "Ok!", INPUT_STATES.NEUTRAL];
      }
      if (value !== "") {
        return [true, "Ok!", INPUT_STATES.NEUTRAL];
      } else {
        return [false, "Required", INPUT_STATES.ERROR];
      }
    };
    passesRegex = function() {
      var message, ref, regex;
      if (regexName == null) {
        return [true, "Ok!", INPUT_STATES.NEUTRAL];
      }
      ref = validationRegexes[regexName], regex = ref.regex, message = ref.message;
      if (regex === void 0) {
        console.error(regexName + " was not found in the validationRegexes dictionary.");
        return [true, "Ok!", INPUT_STATES.NEUTRAL];
      }
      if (regex.test(value)) {
        return [true, "Ok!", INPUT_STATES.SUCCESS];
      } else {
        return [false, message, INPUT_STATES.ERROR];
      }
    };
    passesWarning = function() {
      var filter, message, ref;
      if (warningName == null) {
        return [true, "Ok!", INPUT_STATES.NEUTRAL];
      }
      ref = validationWarnings[warningName], filter = ref.filter, message = ref.message;
      if (filter === void 0) {
        console.error(warningName + " was not found in the validationWarnings dictionary.");
        return [true, "Ok!", INPUT_STATES.NEUTRAL];
      }
      if (filter(value)) {
        return [false, message, INPUT_STATES.WARNING];
      } else {
        return [true, "Ok!", INPUT_STATES.NEUTRAL];
      }
    };
    validationResults = function() {
      var hasPassed, i, len, message, ref, ref1, state;
      ref = [passesRequiredness(), passesRegex(), passesWarning()];
      for (i = 0, len = ref.length; i < len; i++) {
        ref1 = ref[i], hasPassed = ref1[0], message = ref1[1], state = ref1[2];
        if (!hasPassed) {
          return [message, state];
        }
      }
      return ["Ok!", INPUT_STATES.SUCCESS];
    };
    ref = validationResults(), message = ref[0], state = ref[1];
    $input.parent().parent().removeClass("" + bootstrapStateClasses).addClass(state.bootstrapClass);
    $input.parent().attr({
      "data-hint": message
    }).removeClass("" + hintStateClasses).addClass(state.hintClass);
    return state === INPUT_STATES.NEUTRAL || state === INPUT_STATES.SUCCESS;
  };

  checkInputs = function(form) {
    var allValid, i, input, inputs, len, showTooltip;
    showTooltip = function(elem) {
      return elem.addClass("hint--always").hover(function(event) {
        return $(event.currentTarget).removeClass("hint--always");
      });
    };
    inputs = $(form).find("input").slice(1);
    allValid = true;
    for (i = 0, len = inputs.length; i < len; i++) {
      input = inputs[i];
      if (!validateInput(input)) {
        showTooltip($(input).parent());
        allValid = false;
      }
    }
    return allValid;
  };

}).call(this);

//# sourceMappingURL=script.js.map

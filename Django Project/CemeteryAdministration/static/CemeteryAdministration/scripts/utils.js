// "abc def".contains("bc") => true
String.prototype.contains = function(it, caseInsensitive) {
    if (caseInsensitive)
        return this.toUpperCase().indexOf(it.toUpperCase()) != -1;
    return this.indexOf(it) != -1;
};

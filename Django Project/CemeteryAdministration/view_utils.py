import re
from datetime import date
from .forms import YearsForm


def name_to_template(name, html=True):
    """
    :param html: whether to use the html formatting (/ and .html at the end)
    :return: string containing formatted template
    """
    app_name = 'CemeteryAdministration'
    if html:
        return '{0}/{1}.html'.format(app_name, name)
    else:
        return '{0}:{1}'.format(app_name, name)


#
# Table helpers
#


class Table:
    def __init__(self, yr, rws):
        self.year = yr
        self.rows = rws


class TableHeader:
    def __init__(self, name, width):
        self.name = name
        self.width = width


def spot_headers(iw=1, pw=1, rw=1, cw=1):
    return [TableHeader('#', iw), TableHeader('Parcelă', pw), TableHeader('Rând', rw), TableHeader('Loc', cw)]


def person_headers(fw=4, lw=4):
    return [TableHeader('Prenume', fw), TableHeader('Nume', lw)]


#
# Form helpers
#


def years_form(request):
    """
    :return: empty form if invalid or filled form if it was filled
    """
    form = YearsForm(request.GET)
    if form.is_valid():
        return form
    # if the data is empty/invalid, return an empty form
    else:
        return YearsForm()


year_threshold = 50


def shortcut_to_year(shorcut):
    """
    :param shorcut: number representing shorcut
    :return: formal shorcut (ex 15 => 2015, 94 => 1994, 2006 => 2006)
    """
    # 15 => 2015
    if 0 <= shorcut <= year_threshold:
        return 2000 + shorcut
    # 94 => 1994
    elif year_threshold < shorcut < 100:
        return 1900 + shorcut
    else:
        return shorcut


def year_to_shortcut(year):
    """
    reverse of shortcut to year
    """
    if 2000 <= year <= 2000 + year_threshold:
        return year - 2000
    elif 1900 < year < 2000:
        return year - 1900
    else:
        return year


def years_list(form):
    """
    :return: years extracted from the form
    """
    if form.is_valid():
        yrs_str = form.cleaned_data['ani']
        # extract the numbers from the string containing spaces, commas and apostrophes
        yrs_list = list(map(int, re.findall('\d+', yrs_str)))
        # convert each 15 to 2015 and so on
        return list(map(shortcut_to_year, yrs_list))
    else:
        # by default, show only the current year
        return [date.today().year]

#
# Misc utils
#


def collapse_names(names):
    """
    :param names: list of strings
    :return: just one name if they are all the same, otherwise, the names separated by comma
    """
    if all(n == names[0] for n in names):
        return names[0]
    else:
        return ', '.join(names)

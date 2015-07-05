from django.shortcuts import render
from .models import *
from .forms import YearsForm
import re
from datetime import date


def name_to_template(name):
    app_name = 'CemeteryAdministration'
    return '{0}/{1}.html'.format(app_name, name)


def index(request):
    return render(request, name_to_template('index'))


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


def person_headers(fw=2, lw=2):
    return [TableHeader('Prenume', fw), TableHeader('Nume', lw)]


#
# Form helpers
#

def years_form(request):
    form = YearsForm(request.GET)
    if form.is_valid():
        return form
    # if the data is empty/invalid, return an empty form
    else:
        return YearsForm()


def fuzzy_year(yr):
    """
    :param yr: number representing year
    :return: formal year (ex 15 => 2015, 94 => 1994)
    """
    threshold = 50
    # 15 => 2015
    if yr <= threshold:
        return 2000 + yr
    # 94 => 1994
    if threshold < yr < 100:
        return 1900 + yr
    return yr


def years_list(form):
    if form.is_valid():
        yrs_str = form.cleaned_data['ani']
        # extract the numbers from the string containing spaces, commas and apostrophes
        yrs_list = list(map(int, re.findall('\d+', yrs_str)))
        # convert each 15 to 2015 and so on
        return list(map(fuzzy_year, yrs_list))
    else:
        # by default, show only the current year
        return[date.today().year]


def general_register(request):
    return render(request, name_to_template('general_register'))


def spots(request):
    return render(request, name_to_template('spot'))


def spot_detail(request, spot_id):
    return render(request, name_to_template('spot_detail'), {'spot_id': spot_id, })


def ownerships(request):
    return render(request, name_to_template('ownerships'))


def constructions(request):
    return render(request, name_to_template('constructions'))


def operations(request):

    table_headers = spot_headers() + person_headers(3, 3) + [TableHeader('Tip', 1), TableHeader('Notă', 1)]
    max_data_widths = list(map(lambda x: x.width * 10, table_headers))

    form = years_form(request)
    years = years_list(form)

    tables = []
    for year in years:
        opers = Operation.objects.filter(date__year=year)
        rows = []
        for o in opers:
            rows.append(o.spot.identif() +
                        [o.first_name, o.last_name, o.get_type_display(), o.note])
        tables.append(Table(year, rows))

    context = {
        'title': 'Operații',
        'table_headers': table_headers,
        'tables': tables,
        'years_form': form,
        'max_data_widths': max_data_widths,
    }
    return render(request, name_to_template('operations'), context)


def revenue(request):
    return render(request, name_to_template('revenue'))


def maintentance(request):
    # TODO ownerS!!! there can be more owners
    def maintenance_to_owner(maintenance):
        spot = maintenance.spot
        deeds = spot.ownership_deeds.all().order_by('-date')  # most recent first
        d = deeds[0]
        owners = d.owner_set.all()
        return owners[0].identif()

    # the same headers for every table
    table_headers = spot_headers() + person_headers(3, 3) + [TableHeader('Nivel Întreținere', 2)]
    # data is allowed as much as ten times the column width
    max_data_widths = list(map(lambda x: x.width * 10, table_headers))


    form = years_form(request)
    years = years_list(form)

    # build a table for each year in the list
    tables = []
    for year in years:
        maintentances = MaintenanceLevel.objects.filter(year=year)
        rows = []
        for m in maintentances:
            rows.append(m.spot.identif() +
                        maintenance_to_owner(m) +
                        [m.get_description_display()])
        tables.append(Table(year, rows))

    context = {
        'title': 'Întreținere',
        'table_headers': table_headers,
        'tables': tables,
        'years_form': form,
        'max_data_widths': max_data_widths,
    }
    return render(request, name_to_template('maintenance'), context)


def administration(request):
    table_headers = ['#', 'Parcela', 'Rand', 'Loc']
    row1 = ['1', '1a', '1', '1bis']
    row2 = ['2', '2a', '100', '3']
    row3 = ['3', '5a', '67', '1B']
    table_rows = [row1, row2, row3]
    context = {
        'table_headers': table_headers,
        'table_rows': table_rows,
    }
    return render(request, name_to_template('administration'), context)

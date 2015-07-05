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
    return render(request, name_to_template('operations'))


def revenue(request):
    return render(request, name_to_template('revenue'))


spot_headers = ['#', 'Parcelă', 'Rând', 'Loc']
person_headers = ['Nume', 'Prenume']


def maintentance(request):
    # TODO ownerS!!! there can be more owners
    def maintenance_to_owner(maintenance):
        spot = maintenance.spot
        deeds = spot.ownership_deeds.all().order_by('-date')  # most recent first
        d = deeds[0]
        owners = d.owner_set.all()
        return owners[0].identif()

    # todo add popup explaining this behaviour
    def fuzzy_year(yr):
        """
        :param yr: number representing year
        :return: formal year (ex 15 => 2015, 94 => 1994)
        """
        year_breakpoint = 50
        # 15 => 2015
        if yr <= year_breakpoint:
            return 2000 + yr
        # 94 => 1994
        if year_breakpoint < yr < 100:
            return 1900 + yr
        return yr

    class Table:
        def __init__(self, yr, rws):
            self.year = yr
            self.rows = rws

    # the same headers for every table
    table_headers = spot_headers + person_headers + ['Nivel Întreținere']

    form = YearsForm(request.GET)
    if form.is_valid():
        years_str = form.cleaned_data['ani']
        # extract the numbers from the string containing spaces, commas and apostrophes
        years_list = list(map(int, re.findall('\d+', years_str)))
        # converting each 15 to 2015 and so on
        years_list = list(map(fuzzy_year, years_list))
    else:
        # by default, show only the current year
        years_list = [date.today().year]

    # build a table for each year in the list
    tables = []
    for year in years_list:
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
        'years_form': YearsForm(),
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

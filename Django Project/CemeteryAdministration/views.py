from django.shortcuts import render
from .models import *
from .forms import YearsForm
import re
from datetime import date


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
    """
    :return: empty form if invalid or filled form if it was filled
    """
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
    """
    :return: years extracted from the form
    """
    if form.is_valid():
        yrs_str = form.cleaned_data['ani']
        # extract the numbers from the string containing spaces, commas and apostrophes
        yrs_list = list(map(int, re.findall('\d+', yrs_str)))
        # convert each 15 to 2015 and so on
        return list(map(fuzzy_year, yrs_list))
    else:
        # by default, show only the current year
        return [date.today().year]


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


def annual_table(request, title, name, table_headers, entites_filter, entity_data):
    """
    :param request: http request
    :param title: external page title and header
    :param name: internal page name
    :param table_headers: list containing TableHeaders (not including spot headers)
    :param entites_filter: function that takes year as an argument
    :param entity_data: function that takes an entity and returns list of data about it (not including spot identifiers)
    :return: render of the completed template
    """

    table_headers = spot_headers() + table_headers

    # data is allowed as much as ten times the column width
    max_data_widths = list(map(lambda x: x.width * 10, table_headers))

    # show the form and/or extract the years from it
    form = years_form(request)
    years = years_list(form)

    # build a table for each year in the list
    tables = []
    for year in years:
        # get the entities corresponding to that year
        entities = entites_filter(year)
        rows = []
        for entity in entities:
            # show the data for each entitiy
            rows.append(entity.spot.identif() +
                        entity_data(entity))
        tables.append(Table(year, rows))

    context = {
        'template_name': name_to_template(name, html=False),
        'title': title,
        'years_form': form,
        'max_data_widths': max_data_widths,
        'table_headers': table_headers,
        'tables': tables
    }
    return render(request, name_to_template(name, html=True), context)


def operations(request):
    return annual_table(
        request=request,
        name='operations',
        title='Operații',
        table_headers=person_headers(3, 3) + [TableHeader('Tip', 1), TableHeader('Notă', 1)],
        entites_filter=lambda year: Operation.objects.filter(date__year=year),
        entity_data=lambda o: [o.first_name, o.last_name, o.get_type_display(), o.note]
    )


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

    return annual_table(
        request=request,
        name='maintenance',
        title='Întreținere',
        table_headers=person_headers(3, 3) + [TableHeader('Nivel Întreținere', 2)],
        entites_filter=lambda year: MaintenanceLevel.objects.filter(year=year),
        entity_data=lambda m: maintenance_to_owner(m) + [m.get_description_display()]
    )


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

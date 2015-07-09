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
            spot = entity.spot if hasattr(entity, 'spot') else entity.remote_spot()
            rows.append(spot.identif() +
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


def ownerships(request):
    def get_owner(d):
        owner = d.owners.all()[0]
        return owner.identif()

    def other_spots_on_deed(d):
        others = list(d.spots.all())
        others.remove(d.remote_spot())
        return '; '.join(list(map(str, others)))

    return annual_table(
        request=request,
        name='ownerships',
        title='Concesiuni',
        table_headers=person_headers(2, 2) + [TableHeader('Act', 1), TableHeader('Chitanță', 1),
                                              TableHeader('Pe Același Act', 2)],
        entites_filter=lambda year: OwnershipDeed.objects.filter(date__year=year),
        #fixme which owner should be put here?
        entity_data=lambda d: get_owner(d) + [d, d.receipt, other_spots_on_deed(d)]
    )


def constructions(request):
    def constructor_display(construction):
        if construction.owner_builder is not None:
            # FIXME this actually gets italicized in js + css (do this in template language at least)
            return '*' + construction.owner_builder.full_name()
        else:
            return construction.construction_company.name

    def other_constructions_on_auth(c):
        # take only constructions on the same authorization that are different from this one
        others = list(c.construction_authorization.constructions.all())
        if c in others:
            others.remove(c)

        # semicolon separated constructions (condensed info of them)
        return '; '.join(list(map(condensed_info, others)))

    def condensed_info(c):
        return '{0} pe {1}'.format(c.get_type_display(), c.remote_spot())

    return annual_table(
        request=request,
        name='constructions',
        title='Construcții',
        table_headers=[TableHeader('Tip', 1), TableHeader('Constructor', 3), TableHeader('Autorizațe', 1),
                       TableHeader('Pe Aceeași Autorizațe', 3)],
        entites_filter=lambda year: Construction.objects.filter(construction_authorization__date__year=year),
        # todo o autorizatie poate fi pe mai multe locuri
        # pe care o alegem sa reprezinte constructia?
        entity_data=lambda c: [c.get_type_display(), constructor_display(c), c.construction_authorization,
                               other_constructions_on_auth(c)],
    )


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
    return annual_table(
        request=request,
        name='revenue',
        title='Încasări',
        table_headers=[TableHeader('Valoare Contribuție', 4), TableHeader('Chitanță', 4)],
        entites_filter=lambda year: YearlyPayment.objects.filter(year=year),
        entity_data=lambda p: [p.value, str(p.receipt)]
    )


def maintentance(request):
    # FIXME ownerS!!! there can be more owners
    def maintenance_to_owner(maintenance):
        spot = maintenance.spot
        deeds = spot.ownership_deeds.all().order_by('-date')  # most recent first
        d = deeds[0]
        owners = d.owners.all() # this was d.owner_set.all()
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
    # todo administration
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

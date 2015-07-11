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
    # todo splash page (and login)
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


def owners_to_names(owners):
    names = []
    # add every owner to the list
    for owner in owners:
        names.append(owner.full_name())
    return ', '.join(names)


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
    # todo
    return render(request, name_to_template('general_register'), {'title': 'Registru General'})


def spots(request):
    #todo
    return render(request, name_to_template('spot'))


def spot_detail(request, spot_id):
    return render(request, name_to_template('spot_detail'), {'spot_id': spot_id, 'title': 'Fișă Individuală'})


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

    def spot_identif(ent):
        if hasattr(ent, 'spot'):
            return ent.spot.identif()
        elif hasattr(ent, 'remote_spot'):
            return ent.remote_spot().identif()
        else:
            return ent.identif()

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
            rows.append(spot_identif(entity) +
                        entity_data(entity, year))
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


def spots_with_deed_in_year(year, or_before=False):
    spts = []
    for spot in Spot.objects.all():
        for deed in spot.ownership_deeds.all():
            if deed.date.year == year or (or_before and deed.date.year < year):
                spts.append(spot)
                break
    return spts


def ownerships(request):
    def ownership_data_for_spot(spot, year):
        # the most recent deed (that existed in the year in question)
        d = spot.ownership_deeds.filter(date__lte=date(year, 12, 31)).order_by('-date')[0]

        # the most recent receipt
        receipt = d.receipts.order_by('-date')[0]

        # other owners on the same deed
        owners = d.owners.all()
        others = list(d.spots.all())
        others.remove(spot)
        others_disp = ', '.join([str(o) for o in others])

        return [owners_to_names(owners), str(d), str(receipt), others_disp]

    return annual_table(
        request=request,
        name='ownerships',
        title='Concesiuni',
        table_headers=[TableHeader('Concesionari', 4), TableHeader('Act', 1), TableHeader('Chitanță', 1),
                       TableHeader('Pe Același Act', 2)],
        entites_filter=spots_with_deed_in_year,
        entity_data=ownership_data_for_spot
    )


def constructions(request):
    def constructor_display(construction):
        if construction.owner_builder is not None:
            return construction.owner_builder.full_name()
        else:
            company = construction.construction_company.name
            # we use this special mark so we can know what to italicize
            # also for a human to better distingusih between companies and human constructors
            special = '.'
            if not special in company:
                company += special
            return company

    def other_constructions_on_auth(c):
        # take only constructions on the same authorization that are different from this one
        others = list(c.construction_authorization.constructions.all())
        if c in others:
            others.remove(c)

        # semicolon separated constructions (condensed info of them)
        return ', '.join(list(map(condensed_info, others)))

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
        entity_data=lambda c, yr: [c.get_type_display(), constructor_display(c), c.construction_authorization,
                                   other_constructions_on_auth(c)],
    )


def operations(request):
    # todo add year!!!
    return annual_table(
        request=request,
        name='operations',
        title='Înhumări',
        table_headers=person_headers(2, 2) + [TableHeader('Tip', 1), TableHeader('Notă', 4)],
        entites_filter=lambda year: Operation.objects.filter(date__year=year),
        entity_data=lambda o, yr: [o.first_name, o.last_name, o.get_type_display(), o.note]
    )


def revenue(request):
    # todo add button to show only spots with/without payment
    def payment_data(spot, year):
        try:
            payment = YearlyPayment.objects.filter(year=year).get(spot=spot)
            return [payment.value, str(payment.receipt)]
        except YearlyPayment.DoesNotExist:
            return [0, '-']

    return annual_table(
        request=request,
        name='revenue',
        title='Încasări',
        table_headers=[TableHeader('Valoare Contribuție', 4), TableHeader('Chitanță', 4)],
        entites_filter=lambda yr: spots_with_deed_in_year(yr, or_before=True),
        entity_data=payment_data
    )


def maintentance(request):
    def maintenance_to_owner(maintenance):
        # take the most recent deed
        deed = maintenance.spot.ownership_deeds.order_by('-date')[0]
        owners = deed.owners.order_by('last_name', 'first_name').all()
        return owners_to_names(owners)

    return annual_table(
        request=request,
        name='maintenance',
        title='Întreținere',
        table_headers=[TableHeader('Concesionari', 6), TableHeader('Nivel Întreținere', 2)],
        entites_filter=lambda year: MaintenanceLevel.objects.filter(year=year),
        entity_data=lambda m, yr: [maintenance_to_owner(m), m.get_description_display()]
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

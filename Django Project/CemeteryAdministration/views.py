from django.shortcuts import render
from .models import *
from .forms import YearsForm
import re
from datetime import date
import operator


#TODO remove str(...) from here and instead, call str as as mapping in tests


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


def person_headers(fw=4, lw=4):
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


#
# General register & spot detail
#


def general_register(request):
    return render(request, name_to_template('general_register'), {'title': 'Registru General'})


def spots(request):
    return render(request, name_to_template('spot'))


def spot_detail(request, spot_id):
    return render(request, name_to_template('spot_detail'), {'spot_id': spot_id, 'title': 'Fișă Individuală'})


#
# Annual tables
#


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
    max_data_widths = list(map(lambda x: int(x.width * 6.5), table_headers))

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


def spots_with_attribute_date_comparison_year(attribute, comparison, year):
    """
    :param attribute: ownership_deeds, construction_authorizations etc
    :param comparison: ==, <= etc
    :param year: what to compare date of the attribute to
    :return: list of spots
    """
    ops = {'>': operator.gt,
           '<': operator.lt,
           '>=': operator.ge,
           '<=': operator.le,
           '=': operator.eq,
           '==': operator.eq,
           '!=': operator.ne}
    comp = ops[comparison]

    spts = []
    for spot in Spot.objects.all():
        for attr in getattr(spot, attribute).all():
            if comp(attr.date.year, year):
                spts.append(spot)
                break
    return spts


def ownerships(request):
    def ownership_data(spot, year):
        d = spot.most_recent_deed_up_to(year)

        # the most recent receipt
        receipt = d.receipts.order_by('-date')[0]

        owners = d.owners.all()

        # other owners on the same deed
        others = list(d.spots.all())
        others.remove(spot)
        others_disp = ', '.join([str(o) for o in others])

        return [owners_to_names(owners), phones_if_any(owners), str(d), str(receipt), others_disp]

    def phones_if_any(owners):
        """
        :param: owners list of Owners
        :return: comma separated phone numbers. if there are none, a dash instead
        """
        numbers = []
        for owner in owners:
            if owner.phone is not None:
                numbers.append(owner.phone_display())
        if len(numbers) > 0:
            return ', '.join(numbers)
        else:
            return '-'

    return annual_table(
        request=request,
        name='ownerships',
        title='Concesiuni',
        # todo make widths quanta 1/24 not 1/12
        table_headers=[TableHeader('Concesionari', 8), TableHeader('Telefoane', 4), TableHeader('Act', 2), TableHeader('Chitanță', 2),
                       TableHeader('Pe același act', 4)],
        entites_filter=lambda year: spots_with_attribute_date_comparison_year('ownership_deeds', '==', year),
        entity_data=ownership_data
    )


def collapse_names(names):
    """
    :param names: list of strings
    :return: just one name if they are all the same, otherwise, the names separated by comma
    """
    if all(n == names[0] for n in names):
        return names[0]
    else:
        return ', '.join(names)


def constructions(request):
    def construction_data(spot, year):
        # working under the assumption that there can be only one authorization in a year for a spot
        auth = spot.construction_authorizations.get(date__year=year)

        # constructions sorted by type
        constrs = auth.constructions.order_by('type')
        constrs_types = ', '.join([c.get_type_display() for c in constrs])

        constructors = [c.constructor() for c in constrs]

        others = list(auth.spots.all())
        others.remove(spot)
        others_info = ', '.join([str(s) for s in others])

        return [constrs_types, collapse_names(constructors), str(auth), others_info]

    return annual_table(
        request=request,
        name='constructions',
        title='Construcții',
        table_headers=[TableHeader('Tip', 2), TableHeader('Firmă', 8), TableHeader('Autorizațe', 2),
                       TableHeader('Pe aceeași autorizațe', 8)],
        entites_filter=lambda year: spots_with_attribute_date_comparison_year('construction_authorizations', '==', year),
        entity_data=construction_data,
    )


def operations(request):
    return annual_table(
        request=request,
        name='operations',
        title='Înhumări',
        table_headers=person_headers(4, 4) + [TableHeader('Tip', 2), TableHeader('An', 2), TableHeader('Notă', 8)],
        entites_filter=lambda year: Operation.objects.filter(date__year=year),
        entity_data=lambda o, yr: [o.first_name, o.last_name, o.get_type_display(), o.date.year, o.note]
    )


def revenue(request):
    # todo add button to show only spots with/without payment
    def payment_data(spot, year):
        try:
            payment = YearlyPayment.objects.filter(year=year).get(spot=spot)
            return [payment.value, str(payment.receipt)]
        # means it was not paid that year (but we know it was owned)
        except YearlyPayment.DoesNotExist:
            return [0, '-']

    return annual_table(
        request=request,
        name='revenue',
        title='Încasări',
        table_headers=[TableHeader('Valoare', 10), TableHeader('Chitanță', 10)],
        entites_filter=lambda year: spots_with_attribute_date_comparison_year('ownership_deeds', '<=', year),
        entity_data=payment_data
    )


def maintentance(request):
    def maintenance_to_owners(maintenance, year):
        # if there is than one deed change for a spot in a year, only the latest one will show
        deed = maintenance.spot.most_recent_deed_up_to(year)
        owners = deed.owners.order_by('last_name', 'first_name').all()
        return owners_to_names(owners)

    return annual_table(
        request=request,
        name='maintenance',
        title='Întreținere',
        table_headers=[TableHeader('Concesionari', 16), TableHeader('Nivel întreținere', 4)],
        entites_filter=lambda year: MaintenanceLevel.objects.filter(year=year),
        entity_data=lambda m, yr: [maintenance_to_owners(m, yr), m.get_description_display()]
    )


#
# Administration
#


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

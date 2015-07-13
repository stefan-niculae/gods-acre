from django.shortcuts import render, get_object_or_404
from .view_contents import *


#TODO remove str(...) from here and instead, call str as as mapping in tests


def index(request):
    return render(request, name_to_template('index'))


def general_register(request):
    return render(request, name_to_template('general_register'), {'title': 'Registru General'})


def spots(request):
    return render(request, name_to_template('spot'))


def spot_detail(request, spot_id):
    spot = get_object_or_404(Spot, pk=spot_id)

    # todo notice when one of these is empty
    # todo highlight latest item in each category
    deeds = []
    # todo check whether there should be an order by every time *.objects is called
    for deed in OwnershipDeed.objects.order_by('-date'):
        if spot in deed.spots.all():
            deeds.append(deed)
    owners = [ownership_data_from_deed(spot, d) for d in deeds]

    opers = [operation_data(o, None, include_year=True) for o in Operation.objects.filter(spot=spot).order_by('-date')]

    pays = YearlyPayment.objects.filter(spot=spot).order_by('-year')
    payments = [payment_data_list(p, include_year=True) for p in pays]

    auths = []
    for auth in ConstructionAuthorization.objects.order_by('-date'):
        if spot in auth.spots.all():
            auths.append(auth)
    constrs = [construction_data_from_auth(spot, a, include_others=False) for a in auths]

    oldest_deed = deeds[-1]
    kept_years = MaintenanceLevel.objects.filter(spot=spot).values_list('year', flat=True)
    unkept_years = []
    for year in range(date.today().year, oldest_deed.date.year - 1, -1):
        # todo this can be done more efficiently
        if year not in kept_years:
            unkept_years.append(year)

    context = {
        'title': 'Fișă Individuală (istoric)',
        'spot': spot,
        'owners': owners,
        'operations': opers,
        'payments': payments,
        'last_year_paid': pays[0].year,
        'constructions': constrs,
        'unkept_years': unkept_years
    }
    return render(request, name_to_template('spot_detail'), context)


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
    max_data_widths = list(map(lambda x: int(x.width * 6.8), table_headers))

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


def ownerships(request):
    return annual_table(
        request=request,
        name='ownerships',
        title='Concesiuni',
        table_headers=[TableHeader('Concesionari', 7), TableHeader('Telefoane', 5), TableHeader('Act', 2), TableHeader('Chitanțe', 3),
                       TableHeader('Pe același act', 3)],
        entites_filter=lambda year: spots_with_attribute_date_comparison_year('ownership_deeds', '==', year),
        entity_data=ownership_data
    )


def constructions(request):
    return annual_table(
        request=request,
        name='constructions',
        title='Construcții',
        table_headers=[TableHeader('Tip', 2), TableHeader('Constructor', 8), TableHeader('Autorizațe', 2),
                       TableHeader('Pe aceeași autorizațe', 8)],
        entites_filter=lambda year: spots_with_attribute_date_comparison_year('construction_authorizations', '==', year),
        entity_data=construction_data,
    )


def operations(request):
    return annual_table(
        request=request,
        name='operations',
        title='Înhumări',
        table_headers=person_headers(4, 4) + [TableHeader('Tip', 2), TableHeader('Notă', 10)],
        entites_filter=lambda year: Operation.objects.filter(date__year=year),
        entity_data=operation_data
    )


def revenue(request):
    return annual_table(
        request=request,
        name='revenue',
        title='Încasări',
        table_headers=[TableHeader('Valoare', 10), TableHeader('Chitanță', 10)],
        entites_filter=lambda year: spots_with_attribute_date_comparison_year('ownership_deeds', '<=', year),
        entity_data=payment_data
    )


def maintentance(request):
    return annual_table(
        request=request,
        name='maintenance',
        title='Întreținere',
        table_headers=[TableHeader('Concesionari', 16), TableHeader('Nivel întreținere', 4)],
        entites_filter=lambda year: MaintenanceLevel.objects.filter(year=year),
        entity_data=maintenance_data
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

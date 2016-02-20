# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from .view_contents import *
#from django_ajax.decorators import ajax

from django.http import HttpResponse
from simple_rest import Resource
import json


#TODO remove str(...) from here and instead, call str as as mapping in tests


def index(request):
    return render(request, name_to_template('index'))


def general_register(request):
    def join_constr_types(constrs):
        return ', '.join([c.get_type_display() for c in constrs])

    # todo dash if any of these is empty!!

    # todo search form (and pagination)
    rows = []
    for spot in Spot.objects.all():
        # todo check if there is no act (do it more efficiently and also treat it better)
        # get the most recent act
        deeds = []
        for d in OwnershipDeed.objects.order_by('-date'):
            if spot in d.spots.all():
                deeds.append(d)

        if len(deeds) > 0:
            deed = deeds[0]
        else:
            break
        owners = deed.owners.all()
        # todo refactor filtering to deed date into one thing
        opers = spot.operations.all().filter(date__gte=deed.date).order_by('-date')
        auths = []
        # todo models order... so that you don't have to write order_by for everything
        for auth in ConstructionAuthorization.objects.filter(date__gte=deed.date).order_by('-date'):
            if spot in auth.spots.all():
                auths.append(auth)

        # todo refactor this atrocity
        constr_types = [join_constr_types(Construction.objects.filter(construction_authorization=a)) for a in auths]

        row = [[spot.id], [spot.parcel], [spot.row], [spot.column],
               persons_to_names(owners, as_list=True), owners_to_phones(owners, as_list=True),  # todo align each phone with its owner
               [deed], deed.receipts.all(),
               persons_to_names(opers, as_list=True), ['{}{}'.format(o.date.year, o.get_type_display()[0]) for o in opers],
               # todo preference bordura, cavou 1/2001 or bordura 1/2001, cavou 1/2001 on different lines
               constr_types, auths,
               [last_paid(spot, deed)],
               [', '.join([str(year_to_shortcut(y)) for y in unkept_years(spot, deed)])]
               ]
        rows.append(row)

    context = {
        'title': 'Registru General',
        'rows': rows
    }
    return render(request, name_to_template('general_register'), context)


def spots(request):
    return render(request, name_to_template('spot'))


def spot_detail(request, spot_id):
    # todo prettify 404 page
    spot = get_object_or_404(Spot, pk=spot_id)

    # todo notice when one of these is empty!!!
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

    context = {
        'title': 'Fișă Individuală (istoric)',
        'spot': spot,
        'owners': owners,
        'operations': opers,
        'payments': payments,
        'last_year_paid': last_paid(spot),
        'constructions': constrs,
        'unkept_years': unkept_years(spot, oldest_deed)
    }
    return render(request, name_to_template('spot_detail'), context)


#
# Annual tables
#


def annual_table(request, title, name, table_headers, entites_filter, entity_data):
    """
    :param request: http request
    :param title: external page title and header (showed on the page)
    :param name: internal page name (used in form submission)
    :param table_headers: list containing TableHeaders (not including spot headers)
    :param entites_filter: function that takes year as an argument and returns a query set of apropriate entities
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

    # text max length is 7 times each column width
    max_data_widths = list(map(lambda x: int(x.width * 7), table_headers))

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


# Used to identify the field name when sending back from the front-end
class TraceableData:
    def __init__(self, entity, db_id, field, data):
        self.entity = entity
        self.field = field
        self.db_id = db_id
        self.data = data


def spots_administration(request):
    headers = ['#', 'Parcela', 'Rand', 'Loc', 'Nota']
    fields = ['id', 'parcel', 'row', 'column', 'note']
    rows = []
    for spot in Spot.objects.all():
        row = [TraceableData('Spot', spot.id, field, getattr(spot, field)) for field in fields]
        rows.append(row)

    context = {
        'title': 'Administrare locuri de veci',
        'headers': headers,
        'rows': rows,
    }
    return render(request, name_to_template('spots_administration'), context)


def companies_administration(request):
    headers = ['Nume']
    fields = ['name']
    rows = []
    for company in ConstructionCompany.objects.all():
        row = [TraceableData('ConstructionCompany', company.id, field, getattr(company, field)) for field in fields]
        rows.append(row)

    context = {
        'title': 'Administrare companii de constructii',
        'headers': headers,
        'rows': rows,
    }
    return render(request, name_to_template('spots_administration'), context)


# @ajax
def save(request):
    entity  = request.POST.get('entity',    'NO ENTITY')
    db_id   = request.POST.get('db_id',     'NO ID')
    field   = request.POST.get('field',     'NO FIELD')
    data    = request.POST.get('data',      'NO DATA')

    try:
        obj = globals()[entity].objects.get(id=int(db_id))
        setattr(obj, field, data)
        obj.save()
        return 'SUCCESS'
    except:  # TODO check what exceptions this can throw
        print('>' * 25, 'Error running update statement!')
        return 'ERROR'


def rev_js_grid(request):
    return render(request, 'revenue_jsgrid.html')

# todo replace this name
class RevenueJsGrid(Resource):

    def get(self, request):
        spots = Spot.objects.all() \
            .filter(parcel__contains=request.GET.get('parcel')) \
            .filter(row__contains=request.GET.get('row')) \
            .filter(column__contains=request.GET.get('column'))
            # TODO id aswell?

        infos = []
        for s in spots:
            infos.append(
                {
                    'model': 'RevenueInfo',
                    'pk': s.id,
                    'fields': {
                        'parcel': s.parcel,
                        'row': s.row,
                        'column': s.column,
                        'year': 2000,
                        'value': 100,
                        'receipt': "1/2000"
                    }
                }
            )

        json_infos = json.dumps(infos, default=lambda o: o.__dict__)
        return HttpResponse(json_infos, content_type='application/json', status=200)




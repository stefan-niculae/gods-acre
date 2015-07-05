from django.shortcuts import render
from .models import *
from .forms import YearsForm


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


person_headers = ['Nume', 'Prenume']


def maintentance(request):
    # TODO ownerS!!! there can be more owners
    def maintenance_to_owner(maintenance):
        spot = maintenance.spot
        deeds = spot.ownership_deeds.all().order_by('-date')  # most recent first
        d = deeds[0]
        owners = d.owner_set.all()
        return owners[0].identif()

    print('----> method = ', request.method, 'get = ', request.GET)

    year = 2015
    maintentances = MaintenanceLevel.objects.filter(year=year)

    table_headers = person_headers + ['Nivel Întreținere']
    table_rows = []
    for m in maintentances:
        table_rows.append(m.spot.identif() +
                          maintenance_to_owner(m) +
                          [m.get_description_display()])

    context = {
        'table_headers': table_headers,
        'table_rows': table_rows,
        'year': year,
        'title': 'Întreținere',
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

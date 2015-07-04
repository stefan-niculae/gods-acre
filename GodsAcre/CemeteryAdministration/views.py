from django.shortcuts import render
from django.http import HttpResponse


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


def maintentance(request):
    return render(request, name_to_template('maintenance'))


def administration(request):
    table_headers = ['#', 'Parcela', 'Rand', 'Coloana']  # todo ?change coloana to loc
    row1 = ['1', '1a', '1', '1bis']
    row2 = ['2', '2a', '100', '3']
    row3 = ['3', '5a', '67', '1B']
    table_rows = [row1, row2, row3]
    context = {
        'table_headers': table_headers,
        'table_rows': table_rows,
    }
    return render(request, name_to_template('administration'), context)

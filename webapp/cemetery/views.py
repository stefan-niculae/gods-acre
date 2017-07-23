from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, render_to_response
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.translation import ugettext as _
from django.conf import settings

from .forms import ImportForm
from .model_parsers import parse_file
from .models import ALL_MODELS


def test_view(request):
    response = render_to_response('test.html')
    response.set_cookie('django-language', 'ro')
    return response


@staff_member_required
def import_entries(request):
    context = {'form': ImportForm()}
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if not form.is_valid():
            return HttpResponseBadRequest()

        # wipe the database before
        if form.cleaned_data['wipe_beforehand']:
            for model in ALL_MODELS:
                model.objects.all().delete()

        file = form.cleaned_data['document']
        sheet_feedbacks, counts = parse_file(file)
        context['sheet_feedbacks'] = sheet_feedbacks
        context['counts'] = counts
        # TODO: link instead of plain textual representation for add/duplicate feedback

        # messages.success(request, f'{total_successful} entries successfully imported ({total_failed} failed)')  # TODO

    return render(request, 'import-entries.html', context)

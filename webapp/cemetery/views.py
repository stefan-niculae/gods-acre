from django.utils.translation import activate, ugettext_lazy as _

from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

from .forms import ImportForm
from .model_parsers import parse_file
from .models import ALL_MODELS


DYNAMIC_TRANSLATIONS = [_('fail'), _('add'), _('duplicate')]

@staff_member_required
def import_entries(request):
    # TODO properly solve this instead of hard-coding romanian every time
    activate('ro')

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

        totals = {status: sum(count_values[status] for count_values in counts.values())
                  for status in ['add', 'fail', 'duplicate']}

        messages.success(request,
             _(f'Finished importing: {totals["add"]} successful, {totals["fail"]} failed, {totals["duplicate"]} duplicates'))

    return render(request, 'import-entries.html', context)

from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

from .forms import UploadFileForm
from .model_parsers import parse_file


@staff_member_required
def import_entries(request):
    context = {'form': UploadFileForm()}
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if not form.is_valid():
            return HttpResponseBadRequest()

        file = request.FILES['file']
        sheet_feedbacks, counts = parse_file(file)
        context['sheet_feedbacks'] = sheet_feedbacks
        context['counts'] = counts
        # TODO: link instead of plain textual representation for add/duplicate feedback

        # messages.success(request, f'{total_successful} entries successfully imported ({total_failed} failed)')  # TODO

    return render(request, 'import-entries.html', context)

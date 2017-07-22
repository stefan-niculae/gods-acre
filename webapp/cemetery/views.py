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
        context['sheet_feedbacks'] = parse_file(file)
        # messages.success(request, f'{total_successful} entries successfully imported ({total_failed} failed)')  # TODO

    return render(request, 'import-entries.html', context)

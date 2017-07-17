from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages

from .forms import UploadFileForm
from .model_parsers import parse_file


def import_entries(request):
    if request.method == 'GET':
        context = {'form': UploadFileForm()}
        return render(request, 'upload_form.html', context)
    else:
        form = UploadFileForm(request.POST, request.FILES)
        if not form.is_valid():
            return HttpResponseBadRequest()

        print('before parse')
        file = request.FILES['file']
        total_successful, total_failed = parse_file(file)

        messages.success(request, f'{total_successful} entries successfully imported ({total_failed} failed)')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))  # same page

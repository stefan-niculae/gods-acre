from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def test_view(request):
    print('>'*5, 'in test view')
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

from django.conf.urls import url
from django.contrib import admin

from .views import import_entries, test_view

urlpatterns = [
    url(r'^', admin.site.urls),
    url(r'^test$', test_view, name='test')
]

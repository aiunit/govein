from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^submit/$', submit, name='submit'),
    url(r'^spy/$', spy, name='spy'),
    url(r'^preview/(?P<pk>\w+)/$', preview, name='preview'),
]

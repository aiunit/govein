from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .views import *

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^submit/$', submit, name='submit'),
    url(r'^spy/$', spy, name='spy'),
    url(r'^preview/(?P<pk>\w+)/$', preview, name='preview'),
]

''' Rest Framework Routers '''

router = DefaultRouter()

router.register('user', UserViewSet)
router.register('group', GroupViewSet)
router.register('comment', CommentViewSet)
router.register('tag', TagViewSet)
router.register('state', StateTransitionViewSet)
router.register('transition', StateTransitionViewSet)

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^api/', include(router.urls)),
]

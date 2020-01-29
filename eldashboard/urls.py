from django.urls import path

from . import views
from . import api_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('list_samples', views.listsamples, name='listsamples'),
    path('sample/<int:sampleid>', views.updatesampleform, name='updatesampleform'),
    path('sample/copy/<int:sampleid>', views.copysampleform, name='copysampleform'),
    path('sample', views.sampleform, name='sampleform'),
    path('api/searchsamples', api_views.searchsamples, name='searchsamples'),
    path('api/linkednotifcationgroups', api_views.linkednotifcationgroups, name='linkednotifcationgroups'),
]

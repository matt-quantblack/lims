from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views
from . import api_views



urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('list_samples', views.listsamples, name='listsamples'),
    path('<int:refid>/list_samples_selection', views.listsamplesselection, name='listsamplesselection'),
    path('list_jobs', views.listjobs, name='listjobs'),
    path('<int:id>/list_job_results', views.listjobresults, name='listjobresults'),
    path('list_clients', views.listclients, name='listclients'),
    path('list_methods', views.listmethods, name='listmethods'),
    path('<int:clientid>/list_contacts', views.listcontacts, name='listcontacts'),

    path('sample/<int:sampleid>', views.updatesampleform, name='updatesampleform'),
    path('sample/copy/<int:sampleid>', views.copysampleform, name='copysampleform'),
    path('sample', views.sampleform, name='sampleform'),
    path('removesample/<int:id>', views.removesample, name='removesample'),

    path('job/<int:id>', views.updatejobform, name='updatejobform'),
    path('job', views.jobform, name='jobform'),
    path('removejob/<int:id>', views.removejob, name='removejob'),

    path('client/<int:id>', views.updateclientform, name='updateclientform'),
    path('client', views.clientform, name='clientform'),
    path('removeclient/<int:id>', views.removeclient, name='removeclient'),

    path('method/<int:id>', views.updatemethodform, name='updatemethodform'),
    path('method', views.methodform, name='methodform'),
    path('removemethod/<int:id>', views.removemethod, name='removemethod'),

    path('<int:clientid>/contact/<int:id>', views.updatecontactform, name='updatecontactform'),
    path('<int:clientid>/contact', views.contactform, name='contactform'),
    path('<int:clientid>/removecontact/<int:id>', views.removecontact, name='removecontact'),
    path('<int:refid>/list_contacts_selection/<int:clientid>', views.listcontactsselection, name='listcontactsselection'),

    path('api/searchsamples', api_views.searchsamples, name='searchsamples'),
    path('api/searchjobs', api_views.searchjobs, name='searchjobs'),
    path('api/searchclients', api_views.searchclients, name='searchclients'),
    path('api/searchmethods', api_views.searchmethods, name='searchmethods'),
    path('api/searchcontacts', api_views.searchcontacts, name='searchcontacts'),
    path('api/linkednotifcationgroups', api_views.linkednotifcationgroups, name='linkednotifcationgroups'),
    path('api/assignsamples', api_views.assignsamples, name='assignsamples'),
    path('api/addsamples', api_views.addsamples, name='addsamples'),
    path('api/saveresults', api_views.saveresults, name='saveresults'),
    path('api/deleteresult', api_views.deleteresult, name='deleteresult'),
    path('api/generatereport', api_views.generatereport, name='generatereport'),
    path('api/deletereport', api_views.deletereport, name='deletereport'),
    path('api/downloadreport', api_views.downloadreport, name='downloadreport'),
    path('api/emailreport', api_views.emailreport, name='emailreport'),
    path('api/uploadreport', api_views.uploadreport, name='uploadreport'),
    path('api/addng', api_views.addng, name='addng'),
    path('api/removeng', api_views.removeng, name='removeng'),
    path('api/addcontacts', api_views.addcontacts, name='addcontacts'),
    path('api/removenotif', api_views.removenotif, name='removenotif'),
    path('api/sendnotif', api_views.sendnotif, name='sendnotif'),
    path('api/markinvoiced', api_views.markinvoiced, name='markinvoiced'),

]

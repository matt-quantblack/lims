from django.shortcuts import render
from django.shortcuts import redirect
from django.db.models import Max
from django.core.files.storage import FileSystemStorage

from .forms import *

from .models import *
from .serializers import serialize_jobsample


def dashboard(request):

    if request.user.is_authenticated == False:
        return redirect('/login')

    newsamples = Sample.objects.filter(notified=False)
    activejobs = Job.objects.filter(status='Open').all()
    jobstoinvoice = Job.objects.filter(status='Sent').all()
    inner_qs = JobSample.objects.values_list('sample_id', flat=True)
    unassignedsamples = Sample.objects.exclude(id__in=inner_qs)

    for j in activejobs:
        tests = []
        for js in j.jobsamples.all():
            matchedtests = SampleTests.objects.filter(jobsample_id=js.id).all()
            for t in matchedtests:
                if t.test.name not in tests:
                    tests.append(t.test.name)
        j.tests = tests

    for j in activejobs:
        print(j.tests)

    return render(request, "dashboard.html", {'newsamples': newsamples, 'activejobs': activejobs,
                                              'jobstoinvoice':jobstoinvoice, 'unassignedsamples': unassignedsamples})

def listsamples(request):
    if request.user.is_authenticated == False:
        return redirect('/login')

    addurl = 'sample'
    apiurl = '/api/searchsamples'
    title = 'Samples'
    columns = [{'name':'EL Ref'},
               {'name':'Client Name'},
               {'name':'Client Ref'},
               {'name':'Batch'},
               {'name':'Sample Name', 'width': 40}]
    renderstring = '<tr onclick="window.location.href=\'sample/{id}\'"><td>{id}</td><td>{client}</td><td>{clientref}</td><td>{batch}</td><td>{name}</td></tr>'

    return render(request, 'lists/tablelist.html',
                  {'addurl': addurl, 'apiurl':apiurl, 'title':title, 'columns': columns,
                   'renderstring': renderstring})

def listsamplesselection(request, refid):
    if request.user.is_authenticated == False:
        return redirect('/login')

    apiurl = '/api/searchsamples'
    title = 'Samples'
    confirmurl = '/api/addsamples'
    backurl = "/job/{}".format(refid)
    columns = [{'name':'EL Ref'},
               {'name':'Client Name'},
               {'name':'Client Ref'},
               {'name':'Batch'},
               {'name':'Sample Name', 'width': 50}]
    renderstring = '<tr id="{id}"><td>{id}</td><td>{client}</td><td>{clientref}</td><td>{batch}</td><td>{name}</td></tr>'

    job = Job.objects.get(id=refid)
    selected = job.jobsamples.all()

    clientname = job.client.name

    samples = []
    for jobsample in selected:
        samples.append(serialize_jobsample(jobsample))

    return render(request, 'lists/selectionlist.html',
                  {'apiurl':apiurl, 'backurl': backurl, 'confirmurl': confirmurl, 'refid': refid, 'title':title, 'columns': columns,
                   'renderstring': renderstring, 'selected': samples, 'initialsearch': clientname, 'initialresults': None})

def listjobs(request):
    if request.user.is_authenticated == False:
        return redirect('/login')

    addurl = 'job'
    apiurl = '/api/searchjobs'
    title = 'Job Record'
    columns = [{'name': 'Job #', 'width': 10},
               {'name': 'Client'},
               {'name': 'Samples', 'width': 50},
               {'name': 'Status'}]
    renderstring = '<tr onclick="window.location.href=\'job/{id}\'"><td>{id}</td><td>{client}</td><td>{jobsamples}</td><td>{status}</td></tr>'

    return render(request, 'lists/tablelist.html',
                  {'addurl': addurl, 'apiurl': apiurl, 'title': title, 'columns': columns,
                   'renderstring': renderstring})

def listjobresults(request, id):
    if request.user.is_authenticated == False:
        return redirect('/login')

    results = SampleTests.objects.filter(jobsample__job__id=id).order_by('test__name').all()
    officers = Users.objects.all()
    locations = Locations.objects.all()

    reporttypes = ReportTypes.objects.filter(testmethods__sampletests__jobsample__job__id=id).distinct()

    reports = JobReports.objects.filter(job_id=id).all()
    jobdata = JobData.objects.filter(job_id=id).all()
    reporttemplates = ReportTemplates.objects.all()

    defaults = {
        'officer': officers.first(),
        'location': locations.first(),
        'reports': reporttypes.first(),
        'jobdata': jobdata.last(),
        'reporttemplate': reporttemplates.last()
    }

    renderstring = '<tr><td><button type="button" class="btn btn-info download_report" reportid="{id}">Download\
    </button><button type="button" class="btn btn-success email_report" reportid="{id}">Email\
    </button></td><td>#{job} - {reportno}</td><td>{name}</td><td><button type="button" \
    class="btn btn-danger delete_report" reportid="{id}">Delete</button></td></tr>'

    return render(request, 'lists/jobresultslist.html', {'results': results,
                                                         'officers': officers,
                                                         'locations': locations,
                                                         'reporttypes': reporttypes,
                                                         'reports': reports,
                                                         'jobdata': jobdata,
                                                         'reporttemplates': reporttemplates,
                                                         'default': defaults,
                                                         'jobid': id,
                                                         'renderstring': renderstring,
                                                         'backurl': '/job/{}'.format(id)})

def listclients(request):
    if request.user.is_authenticated == False:
        return redirect('/login')

    addurl = 'client'
    apiurl = '/api/searchclients'
    title = 'Clients'
    columns = [{'name': 'Client Name'}]
    renderstring = '<tr onclick="window.location.href=\'client/{id}\'"><td>{name}</td></tr>'

    return render(request, 'lists/tablelist.html',
                  {'addurl': addurl, 'apiurl': apiurl, 'title': title, 'columns': columns,
                   'renderstring': renderstring})

def listmethods(request):
    if request.user.is_authenticated == False:
        return redirect('/login')

    addurl = 'method'
    apiurl = '/api/searchmethods'
    title = 'Test Methods'
    columns = [{'name': 'Method Name'}]
    renderstring = '<tr onclick="window.location.href=\'method/{id}\'"><td>{name}</td></tr>'

    return render(request, 'lists/tablelist.html',
                  {'addurl': addurl, 'apiurl': apiurl, 'title': title, 'columns': columns,
                   'renderstring': renderstring})

def listcontacts(request, clientid):
    if request.user.is_authenticated == False:
        return redirect('/login')

    addurl = '/{}/contact'.format(clientid)
    apiurl = '/api/searchcontacts'
    title = 'Contacts'
    columns = [{'name': 'First Name'},
               {'name': 'Last Name'},
               {'name': 'Email'},
               {'name': 'Phone'}]
    renderstring = '<tr onclick="window.location.href=\'contact/{id}\'"><td>{firstname}</td><td>{lastname}</td><td>{email}</td><td>{phone}</td></tr>'

    return render(request, 'lists/tablelist.html',
                  {'addurl': addurl, 'apiurl': apiurl, 'title': title, 'columns': columns,
                   'renderstring': renderstring, "refid": clientid, "backurl": "/client/{}".format(clientid)})

def listcontactsselection(request, refid, clientid):
    if request.user.is_authenticated == False:
        return redirect('/login')

    title = 'Contacts'
    confirmurl = '/api/addcontacts'
    backurl = "/client/{}".format(clientid)
    columns = [{'name':'First Name'},
               {'name':'Last Name'},
               {'name':'Email'},]

    ng = NotificationGroups.objects.get(id=refid)
    selected = ng.contacts.all()

    results = Contacts.objects.filter(client_id=clientid).all()

    results = [x for x in results if x not in selected]

    contacts = []
    for contact in selected:
        contacts.append({'firstname': contact.firstname, 'lastname': contact.lastname, 'email': contact.email})

    return render(request, 'lists/contactselectionlist.html',
                  {'backurl': backurl, 'confirmurl': confirmurl, 'refid': refid, 'title':title, 'columns': columns,
                   'selected': contacts, 'initialresults': results})

def listtemplates(request):
    if request.user.is_authenticated == False:
        return redirect('/login')

    addurl = 'template'
    apiurl = '/api/searchtemplates'
    title = 'Report Templates'
    columns = [{'name': 'Name'},
               {'name': 'Report Type'}]
    renderstring = '<tr onclick="window.location.href=\'template/{id}\'"><td>{name}</td><td>{report_type}</td></tr>'

    return render(request, 'lists/tablelist.html',
                  {'addurl': addurl, 'apiurl': apiurl, 'title': title, 'columns': columns,
                   'renderstring': renderstring})

def updatesampleform(request, sampleid):
    if request.user.is_authenticated == False:
        return redirect('/login')

    sample = Sample.objects.get(id=sampleid)
    sampleform = SampleForm(request.POST or None, instance=sample)
    if request.method == 'POST':
        if sampleform.is_valid():
            sampleform.save()


    return render(request, 'forms/sampleform.html', {"sampleform": sampleform, "id": sample.id})

def insertnewsample(request):
    if request.user.is_authenticated == False:
        return redirect('/login')

    sampleform = SampleForm(request.POST or None)

    # save the form and redirect to the update sample page
    if sampleform.is_valid():
        sample = sampleform.save()

        return sample

    return None

def sampleform(request):
    if request.user.is_authenticated == False:
        return redirect('/login')

    # create the sampleForm object from the posted form data
    if request.method == 'POST':
        sample = insertnewsample(request)
        return redirect('/sample/{}'.format(sample.id))
    #or create a blank form if not a post
    else:
        sampleform = SampleForm()

    return render(request, 'forms/sampleform.html', {"sampleform": sampleform})


def copysampleform(request, sampleid):
    if request.user.is_authenticated == False:
        return redirect('/login')

    if request.method == 'POST':
        sample = insertnewsample(request)
        return redirect('/sample/{}'.format(sample.id))
    else:
        sample = Sample.objects.get(id=sampleid)
        sample.id = None
        sampleform = SampleForm(request.POST or None, instance=sample)

    return render(request, 'forms/sampleform.html', {"sampleform": sampleform})

def removesample(request, id):
    if request.user.is_authenticated == False:
        return redirect('/login')

    Sample.objects.filter(id=id).delete()
    return redirect('/list_samples')


def insertnewclient(request):
    if request.user.is_authenticated == False:
        return redirect('/login')

    form = ClientForm(request.POST or None)

    # save the form and redirect to the update sample page
    if form.is_valid():
        item = form.save()

        return item

    return None

def updateclientform(request, id):
    if request.user.is_authenticated == False:
        return redirect('/login')

    item = Clients.objects.get(id=id)
    contacts = Contacts.objects.filter(client=id)

    form = ClientForm(request.POST or None, instance=item)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('/list_clients')

    ngs = NotificationGroups.objects.prefetch_related('contacts').filter(client_id=id).all()

    renderstring = """<tr><td>{name}</td>
                            <td>{contacts}
                            </td>
                        <td>
                            <div class="float-right">
                                <a href="/{id}/list_contacts_selection/{client}" id="edit_ng" class="btn btn-info">Edit</a>
                                <button ngid="{id}" class="btn btn-danger delete_ng">X</button>
                            </div>

                        </td></tr>"""

    return render(request, 'forms/clientform.html', {"form": form, "contacts": contacts, "notificationgroups": ngs,
                                                     "renderstring": renderstring, "id": item.id})


def clientform(request):
    if request.user.is_authenticated == False:
        return redirect('/login')

    # create the sampleForm object from the posted form data
    if request.method == 'POST':
        item = insertnewclient(request)
        return redirect('/client/{}'.format(item.id))
    #or create a blank form if not a post
    else:
        form = ClientForm()

    return render(request, 'forms/clientform.html', {"form": form})

def removeclient(request, id):
    if request.user.is_authenticated == False:
        return redirect('/login')

    Clients.objects.filter(id=id).delete()
    return redirect('/list_clients')

##############################################################################################

def insertnewtemplate(request):
    if request.user.is_authenticated == False:
        return redirect('/login')


    form = ReportTemplateForm(request.POST, request.FILES)

    # save the form and redirect to the update sample page
    if form.is_valid():

        item = form.save()
        return item

    return None

def updatetemplateform(request, id):
    if request.user.is_authenticated == False:
        return redirect('/login')

    item = ReportTemplates.objects.get(id=id)

    if request.method == 'POST':
        form = ReportTemplateForm(request.POST or None, request.FILES or None, instance=item)
        if form.is_valid():
            form.save()
            return redirect('/list_templates')
    else:
        form = ReportTemplateForm(instance=item)

    return render(request, 'forms/templateform.html', {"form": form, "id": item.id})


def templateform(request):
    if request.user.is_authenticated == False:
        return redirect('/login')

    # create the sampleForm object from the posted form data
    if request.method == 'POST':
        item = insertnewtemplate(request)
        return redirect('/template/{}'.format(item.id))
    #or create a blank form if not a post
    else:
        form = ReportTemplateForm()

    return render(request, 'forms/templateform.html', {"form": form})

def removetemplate(request, id):
    if request.user.is_authenticated == False:
        return redirect('/login')

    ReportTemplates.objects.filter(id=id).delete()
    return redirect('/list_templates')

##############################################################################################

def insertnewjob(request):
    if request.user.is_authenticated == False:
        return redirect('/login')

    form = JobForm(request.POST or None)

    # save the form and redirect to the update sample page
    if form.is_valid():
        item = form.save()

        return item

    return None

def updatejobform(request, id):
    if request.user.is_authenticated == False:
        return redirect('/login')

    item = Job.objects.get(id=id)
    samples = JobSample.objects.filter(job=id)
    reports = JobReports.objects.filter(job=id)
    activity = JobActivity.objects.filter(job=id)
    results = {}
    alltests = TestMethods.objects.all().order_by("name")

    jobsamples = []
    for sample in samples:
        jobsamples.append(serialize_jobsample(sample))

    form = JobForm(request.POST or None, instance=item)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('/list_jobs')


    return render(request, 'forms/jobform.html', {"form": form, "samples": jobsamples, "reports": reports, "activity": activity, "results": results, "tests": alltests, "id": item.id})


def jobform(request):
    if request.user.is_authenticated == False:
        return redirect('/login')

    # create the sampleForm object from the posted form data
    if request.method == 'POST':
        item = insertnewjob(request)
        return redirect('/job/{}'.format(item.id))
    #or create a blank form if not a post
    else:
        form = JobForm()

    return render(request, 'forms/jobform.html', {"form": form})

def removejob(request, id):
    if request.user.is_authenticated == False:
        return redirect('/login')

    Job.objects.filter(id=id).delete()
    return redirect('/list_jobs')

##############################################################################################


def insertnewmethod(request):
    if request.user.is_authenticated == False:
        return redirect('/login')

    form = TestMethodForm(request.POST or None)

    # save the form and redirect to the update sample page
    if form.is_valid():
        item = form.save()

        return item

    return None

def updatemethodform(request, id):
    if request.user.is_authenticated == False:
        return redirect('/login')

    item = TestMethods.objects.get(id=id)

    form = TestMethodForm(request.POST or None, instance=item)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('/list_methods')


    return render(request, 'forms/methodform.html', {"form": form, "id": item.id})


def methodform(request):
    if request.user.is_authenticated == False:
        return redirect('/login')

    # create the sampleForm object from the posted form data
    if request.method == 'POST':
        item = insertnewmethod(request)
        return redirect('/method/{}'.format(item.id))
    #or create a blank form if not a post
    else:
        form = TestMethodForm()

        #get the max test number and increment by one
        max_tm = TestMethods.objects.aggregate(Max('tmnumber'))['tmnumber__max']
        if max_tm:
            numbers = [s for s in max_tm if s.isdigit()]
            new = ""
            for x in numbers:
                new += x
            new_num = int(new) + 1
        else:
            new_num = 1
        form["tmnumber"].initial = new_num


    return render(request, 'forms/methodform.html', {"form": form})

def removemethod(request, id):
    if request.user.is_authenticated == False:
        return redirect('/login')

    TestMethods.objects.filter(id=id).delete()
    return redirect('/list_methods')

#############################################################################################

def insertnewcontact(request, clientid):
    if request.user.is_authenticated == False:
        return redirect('/login')

    print(request.POST)
    form = ContactForm(request.POST or None)

    print(form)
    # save the form and redirect to the update sample page
    if form.is_valid():
        item = form.save()

        return item

    return None


def updatecontactform(request, clientid, id):
    if request.user.is_authenticated == False:
        return redirect('/login')

    item = Contacts.objects.get(id=id)

    form = ContactForm(request.POST or None, instance=item)
    if request.method == 'POST':
        print("HERE", item.client)
        if form.is_valid():
            form.save()
            return redirect('/{}/list_contacts'.format(clientid))

    return render(request, 'forms/contactform.html', {"form": form, "clientid": clientid, "id": item.id})


def contactform(request, clientid):
    if request.user.is_authenticated == False:
        return redirect('/login')

    # create the sampleForm object from the posted form data
    if request.method == 'POST':
        item = insertnewcontact(request, clientid)
        return redirect('/{}/list_contacts'.format(clientid))
    #or create a blank form if not a post
    else:
        form = ContactForm()
        form["client"].initial = clientid
        form["lastname"].initial = ""
        form["phone"].initial = ""

    return render(request, 'forms/contactform.html', {"form": form, "clientid": clientid})

def removecontact(request, clientid, id):
    if request.user.is_authenticated == False:
        return redirect('/login')

    Contacts.objects.filter(id=id).delete()
    return redirect('/{}/list_contacts'.format(clientid))

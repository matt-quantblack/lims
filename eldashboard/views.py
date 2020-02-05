from django.shortcuts import render
from django.shortcuts import redirect
from django.db.models import Max


from .forms import SampleForm
from .forms import ClientForm
from .forms import ContactForm
from .forms import TestMethodForm
from .forms import JobForm

from .models import Sample, Clients, Contacts, TestMethods, Job, JobSample, JobReports, JobActivity, SampleTests
from .serializers import serialize_jobsample


def dashboard(request):
    return render(request, "dashboard.html")

def listsamples(request):

    addurl = 'sample'
    apiurl = '/api/searchsamples'
    title = 'Samples'
    columns = [{'name':'EL Ref'},
               {'name':'Client Name'},
               {'name':'Client Ref'},
               {'name':'Batch'},
               {'name':'Sample Name', 'width': 40},
               {'name':'Attached Reports'}]
    renderstring = '<tr onclick="window.location.href=\'sample/{id}\'"><td>{id}</td><td>{client}</td><td>{clientref}</td><td>{batch}</td><td>{name}</td><td></td></tr>'

    return render(request, 'lists/tablelist.html',
                  {'addurl': addurl, 'apiurl':apiurl, 'title':title, 'columns': columns,
                   'renderstring': renderstring})

def listsamplesselection(request, refid):

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
    print (refid)
    return render(request, 'lists/selectionlist.html',
                  {'apiurl':apiurl, 'backurl': backurl, 'confirmurl': confirmurl, 'refid': refid, 'title':title, 'columns': columns,
                   'renderstring': renderstring})

def listjobs(request):

    addurl = 'job'
    apiurl = '/api/searchjobs'
    title = 'Job Record'
    columns = [{'name': 'Job #', 'width': 10},
               {'name': 'Client'},
               {'name': 'Samples', 'width': 50},
               {'name': 'Status'}]
    renderstring = '<tr onclick="window.location.href=\'job/{id}\'"><td>{id}</td><td>{client}</td><td>{jobsamples}</td><td></td></tr>'

    return render(request, 'lists/tablelist.html',
                  {'addurl': addurl, 'apiurl': apiurl, 'title': title, 'columns': columns,
                   'renderstring': renderstring})


def listclients(request):

    addurl = 'client'
    apiurl = '/api/searchclients'
    title = 'Clients'
    columns = [{'name': 'Client Name'}]
    renderstring = '<tr onclick="window.location.href=\'client/{id}\'"><td>{name}</td></tr>'

    return render(request, 'lists/tablelist.html',
                  {'addurl': addurl, 'apiurl': apiurl, 'title': title, 'columns': columns,
                   'renderstring': renderstring})

def listmethods(request):

    addurl = 'method'
    apiurl = '/api/searchmethods'
    title = 'Test Methods'
    columns = [{'name': 'Method Name'}]
    renderstring = '<tr onclick="window.location.href=\'method/{id}\'"><td>{name}</td></tr>'

    return render(request, 'lists/tablelist.html',
                  {'addurl': addurl, 'apiurl': apiurl, 'title': title, 'columns': columns,
                   'renderstring': renderstring})

def listcontacts(request, clientid):
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


def updatesampleform(request, sampleid):

    sample = Sample.objects.get(id=sampleid)
    sampleform = SampleForm(request.POST or None, instance=sample)
    if request.method == 'POST':
        if sampleform.is_valid():
            sampleform.save()


    return render(request, 'forms/sampleform.html', {"sampleform": sampleform, "id": sample.id})

def insertnewsample(request):
    sampleform = SampleForm(request.POST or None)

    # save the form and redirect to the update sample page
    if sampleform.is_valid():
        sample = sampleform.save()

        return sample

    return None

def sampleform(request):
    # create the sampleForm object from the posted form data
    if request.method == 'POST':
        sample = insertnewsample(request)
        return redirect('/sample/{}'.format(sample.id))
    #or create a blank form if not a post
    else:
        sampleform = SampleForm()

    return render(request, 'forms/sampleform.html', {"sampleform": sampleform})


def copysampleform(request, sampleid):
    if request.method == 'POST':
        sample = insertnewsample(request)
        return redirect('/sample/{}'.format(sample.id))
    else:
        sample = Sample.objects.get(id=sampleid)
        sample.id = None
        sampleform = SampleForm(request.POST or None, instance=sample)

    return render(request, 'forms/sampleform.html', {"sampleform": sampleform})

def removesample(request, id):
    Sample.objects.filter(id=id).delete()
    return redirect('/list_samples')


def insertnewclient(request):
    form = ClientForm(request.POST or None)

    # save the form and redirect to the update sample page
    if form.is_valid():
        item = form.save()

        return item

    return None

def updateclientform(request, id):

    item = Clients.objects.get(id=id)
    contacts = Contacts.objects.filter(client=id)

    form = ClientForm(request.POST or None, instance=item)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('/list_clients')


    return render(request, 'forms/clientform.html', {"form": form, "contacts": contacts, "id": item.id})


def clientform(request):
    # create the sampleForm object from the posted form data
    if request.method == 'POST':
        item = insertnewclient(request)
        return redirect('/client/{}'.format(item.id))
    #or create a blank form if not a post
    else:
        form = ClientForm()

    return render(request, 'forms/clientform.html', {"form": form})

def removeclient(request, id):
    Clients.objects.filter(id=id).delete()
    return redirect('/list_clients')


##############################################################################################

def insertnewjob(request):
    form = JobForm(request.POST or None)

    # save the form and redirect to the update sample page
    if form.is_valid():
        item = form.save()

        return item

    return None

def updatejobform(request, id):

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
    # create the sampleForm object from the posted form data
    if request.method == 'POST':
        item = insertnewjob(request)
        return redirect('/job/{}'.format(item.id))
    #or create a blank form if not a post
    else:
        form = JobForm()

    return render(request, 'forms/jobform.html', {"form": form})

def removejob(request, id):
    Job.objects.filter(id=id).delete()
    return redirect('/list_jobs')

##############################################################################################


def insertnewmethod(request):
    form = TestMethodForm(request.POST or None)

    # save the form and redirect to the update sample page
    if form.is_valid():
        item = form.save()

        return item

    return None

def updatemethodform(request, id):

    item = TestMethods.objects.get(id=id)

    form = TestMethodForm(request.POST or None, instance=item)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('/list_methods')


    return render(request, 'forms/methodform.html', {"form": form, "id": item.id})


def methodform(request):
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
    TestMethods.objects.filter(id=id).delete()
    return redirect('/list_methods')

#############################################################################################

def insertnewcontact(request, clientid):

    print(request.POST)
    form = ContactForm(request.POST or None)

    print(form)
    # save the form and redirect to the update sample page
    if form.is_valid():
        item = form.save()

        return item

    return None


def updatecontactform(request, clientid, id):

    item = Contacts.objects.get(id=id)

    form = ContactForm(request.POST or None, instance=item)
    if request.method == 'POST':
        print("HERE", item.client)
        if form.is_valid():
            form.save()
            return redirect('/{}/list_contacts'.format(clientid))

    return render(request, 'forms/contactform.html', {"form": form, "clientid": clientid, "id": item.id})


def contactform(request, clientid):
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
    Contacts.objects.filter(id=id).delete()
    return redirect('/{}/list_contacts'.format(clientid))

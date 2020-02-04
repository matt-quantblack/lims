from django.shortcuts import render
from django.shortcuts import redirect
from django.http import JsonResponse


from .forms import SampleForm
from .forms import ClientForm
from .forms import ContactForm

from .models import Sample
from .models import Clients
from .models import Contacts
from .models import NotificationGroups


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

    addurl = 'client'
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

from django.db.models import Prefetch
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

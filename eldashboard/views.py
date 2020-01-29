from django.shortcuts import render
from django.shortcuts import redirect
from django.http import JsonResponse

from .forms import SampleForm
from .models import Sample
from .models import NotificationGroups


def dashboard(request):
    return render(request, "dashboard.html")

def listsamples(request):

    return render(request, 'lists/samplelist.html')

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








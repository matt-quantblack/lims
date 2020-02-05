
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import Sample
from .models import Clients
from .models import Contacts
from .models import TestMethods
from .models import NotificationGroups
from .models import Job
from .models import SampleTests, JobSample

from .serializers import SampleSerializer
from .serializers import ClientSerializer
from .serializers import ContactSerializer
from .serializers import TestMethodSerializer
from .serializers import DropDownSerializer
from .serializers import JobListSerializer
from .serializers import serialize_jobsample

from django.shortcuts import redirect

from django.db.models.functions import Cast
from django.db.models import CharField



def linkednotifcationgroups(request):

    #get the client id from the request and convert to an int
    client_id = request.GET.get('client_id', None)
    if client_id is not None and client_id.isnumeric():
        client_id = int(client_id)
    else:
        client_id = -1

    results = NotificationGroups.objects.filter(contacts__client_id=client_id)

    # format queryset into json for returning
    serializer = DropDownSerializer(results, many=True)

    return JsonResponse(serializer.data, safe=False)

def addsamples(request):
    job_id = request.GET.get('refid', None)
    sample_ids = request.GET.get('ids', None)

    if job_id.isnumeric():
        job_id = int(job_id)
        selected = sample_ids.split(',')

        for id in selected:
            if id.isnumeric():
                jobsample = JobSample()
                jobsample.sample_id = id
                jobsample.save()

                job = Job.objects.get(id=job_id)
                job.jobsamples.add(jobsample)

                job.save()

    return JsonResponse({'success': True})

def assignsamples(request):

    job_id = request.GET.get('job_id', None)
    test_id = request.GET.get('test_id', None)
    jobsample_id = request.GET.get('jobsample_id', None) #-1 means all samples for this job


    if jobsample_id is not None and jobsample_id != -1:
        selected = jobsample_id.split(',')
    else:
        selected = []

    samples = []
    jobsamples = Job.objects.get(id=job_id).jobsamples.all()

    for jobsample in jobsamples:

        if jobsample_id == "-1" or str(jobsample.id) in selected:
            sampletest = SampleTests()
            sampletest.jobsample_id = jobsample.id
            sampletest.test_id = test_id
            sampletest.save()

        samples.append(serialize_jobsample(jobsample))

    return render(request, 'includes/jobsample.html',
                  {"samples": samples})


def searchsamples(request):

    query = request.GET.get('q')
    page_size = request.GET.get('page_size', 20)
    page = request.GET.get('page')

    if query:
        results = Sample.objects.filter(Q(id__icontains=query) | \
                                        Q(clientref__icontains=query) | \
                                        Q(name__icontains=query) | \
                                        Q(client__name__icontains=query) | \
                                        Q(batch__icontains=query)).order_by("-received")
    else:
        results = Sample.objects.all().order_by("-received")

    paginator = Paginator(results, page_size)


    try:
        res = paginator.page(page)
    except PageNotAnInteger:
        res = paginator.page(1)
    except EmptyPage:
        res = paginator.page(paginator.num_pages)

    # format queryset into json for returning
    serializer = SampleSerializer(res, many=True)

    context = {
        'data': serializer.data,
        'more': res.has_next()
    }

    return JsonResponse(context)

def searchjobs(request):

    query = request.GET.get('q')
    page_size = request.GET.get('page_size', 20)
    page = request.GET.get('page')

    if query:
        results = Job.objects.annotate(id_str=Cast('jobsample__sample_id', output_field=CharField()),).\
            filter(Q(id__icontains=query) |\
                   Q(client__name__icontains=query) |\
                   Q(id_str__icontains=query) |\
                   Q(jobsample__sample__name__icontains=query)).order_by("-id")

    else:
        results = Job.objects.all().order_by("-id")

    paginator = Paginator(results, page_size)

    try:
        res = paginator.page(page)
    except PageNotAnInteger:
        res = paginator.page(1)
    except EmptyPage:
        res = paginator.page(paginator.num_pages)

    # format queryset into json for returning
    serializer = JobListSerializer(res, many=True)

    context = {
        'data': serializer.data,
        'more': res.has_next()
    }

    return JsonResponse(context)

def searchclients(request):

    query = request.GET.get('q')
    page_size = request.GET.get('page_size', 20)
    page = request.GET.get('page')

    if query:
        results = Clients.objects.filter(name__icontains=query).order_by("name")
    else:
        results = Clients.objects.all().order_by("name")

    paginator = Paginator(results, page_size)

    try:
        res = paginator.page(page)
    except PageNotAnInteger:
        res = paginator.page(1)
    except EmptyPage:
        res = paginator.page(paginator.num_pages)

    # format queryset into json for returning
    serializer = ClientSerializer(res, many=True)

    context = {
        'data': serializer.data,
        'more': res.has_next()
    }

    return JsonResponse(context)

def searchmethods(request):


    query = request.GET.get('q')
    page_size = request.GET.get('page_size', 20)
    page = request.GET.get('page')

    if query:
        results = TestMethods.objects.filter(name__icontains=query).order_by("name")
    else:
        results = TestMethods.objects.all().order_by("name")

    paginator = Paginator(results, page_size)

    try:
        res = paginator.page(page)
    except PageNotAnInteger:
        res = paginator.page(1)
    except EmptyPage:
        res = paginator.page(paginator.num_pages)

    # format queryset into json for returning
    serializer = TestMethodSerializer(res, many=True)

    context = {
        'data': serializer.data,
        'more': res.has_next()
    }

    return JsonResponse(context)


def searchcontacts(request):

    clientid = request.GET.get('refid')
    query = request.GET.get('q')
    page_size = request.GET.get('page_size', 20)
    page = request.GET.get('page')

    print(query)
    if query:
        results = Contacts.objects.filter(Q(client=clientid) & \
                                          (Q(firstname__icontains=query) | \
                                          Q(lastname__icontains=query) | \
                                          Q(email__icontains=query))).order_by("firstname")
    else:
        results = Contacts.objects.filter(client=clientid).order_by("firstname")

    paginator = Paginator(results, page_size)

    try:
        res = paginator.page(page)
    except PageNotAnInteger:
        res = paginator.page(1)
    except EmptyPage:
        res = paginator.page(paginator.num_pages)

    # format queryset into json for returning
    serializer = ContactSerializer(res, many=True)

    context = {
        'data': serializer.data,
        'more': res.has_next()
    }

    return JsonResponse(context)


from django.http import JsonResponse
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import Sample
from .models import Clients
from .models import Contacts
from .models import TestMethods
from .models import NotificationGroups

from .serializers import SampleSerializer
from .serializers import ClientSerializer
from .serializers import ContactSerializer
from .serializers import TestMethodSerializer
from .serializers import DropDownSerializer



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

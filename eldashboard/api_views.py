
from django.http import JsonResponse
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import Sample
from .models import NotificationGroups

from .serializers import SampleSerializer
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

    results = Sample.objects.all().order_by("-received")
    query = request.GET.get('q')
    page_size = request.GET.get('page_size', 20)
    page = request.GET.get('page')

    if query:
        results = Sample.objects.filter(Q(id__icontains=query) | \
                                        Q(clientref__icontains=query) | \
                                        Q(name__icontains=query) | \
                                        Q(client__name__icontains=query) | \
                                        Q(batch__icontains=query)).order_by("-received")

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

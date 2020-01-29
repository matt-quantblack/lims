from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from django.core.paginator import Paginator
from .models import Sample
from .models import Clients
from .models import NotificationGroups
from .models import Contacts
from .models import StorageCategory
from .serializers import SampleSerializer
from .serializers import DropDownSerializer
import datetime
import sys
from django.db.models import Q

# tests for views
class BaseViewTest(APITestCase):
    client = APIClient()


    def setUp(self):

        client = Clients.objects.create(name="Test Client")

        #create some contacts for the client
        contact = Contacts.objects.create(firstname="User", lastname="Lastname", client_id=client.id)

        #create some notifcation groups
        ng = NotificationGroups.objects.create(name="Linked1")
        ng.contacts.set([contact])

        ng2 = NotificationGroups.objects.create(name="Default")
        ng3 = NotificationGroups.objects.create(name="Linked2")
        ng3.contacts.set([contact])

        sg = StorageCategory.objects.create(category="Room Temp.")

        # add test data
        for i in range(30):
            Sample.objects.create(name="Test %d" % i,
                              received=datetime.datetime.now().date(),
                              clientref="clientref%d" % i,
                              batch="batch%d" % i,
                              condition="condition%d" % i,
                              description="desc%d" % i,
                              client_id=client.id,
                              notificationgroup_id=ng.id,
                              storage_id=sg.id)


class GetSamplesTest(BaseViewTest):

    def test_get_linked_notify_groups(self):
        """
        This test ensures that notification groups attached to the client id are returned
        """
        client = Clients.objects.first()
        ng = NotificationGroups.objects.first()

        # hit the API endpoint
        response = self.client.get(reverse('linkednotifcationgroups'), {"client_id": client.id}, format='json')

        expected = NotificationGroups.objects.filter(contacts__client_id=client.id)

        # format queryset into json for returning
        serializer = DropDownSerializer(expected, many=True)

        response_item_count = len(response.json())
        #sys.stderr.write(repr(len(response.json())) + '\n')

        self.assertEqual(response.json(), serializer.data)
        self.assertEqual(response_item_count, 2) #should only be 2 linked notification groups
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_samples(self):

        """
        This test ensures that all samples added in the setUp method
        exist when loop through the pages in the sample list
        """
        page_size = 20

        # hit the API endpoint for both pages
        for page in range(1, 3):

            data = {'page': page,
                    'page_size': page_size}
            response = self.client.get(reverse('searchsamples'), data, format='json')

            expected = Sample.objects.all().order_by("-received")

            paginator = Paginator(expected, page_size)
            res = paginator.page(page)

            # format queryset into json for returning
            serializer = SampleSerializer(res, many=True)

            context = {
                'data': serializer.data,
                'more': (page == 1)
            }

            self.assertEqual(response.json(), context)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_samples(self):

        """
        This test ensures we find a specific sample in the list
        """
        page_size = 20
        query = 'batch8'

        # hit the API endpoint
        data = {'q': query,
                'page': 1,
                'page_size': page_size}
        response = self.client.get(reverse('searchsamples'), data, format='json')

        expected = Sample.objects.filter(batch__icontains=query).order_by("-received")

        # format queryset into json for returning
        serializer = SampleSerializer(expected, many=True)

        context = {
            'data': serializer.data,
            'more': False
        }

        self.assertEqual(response.json(), context)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
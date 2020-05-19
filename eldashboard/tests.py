from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.test import APITestCase, APIClient
from django.test import TestCase
from rest_framework.views import status
from django.core.paginator import Paginator
from .models import *
from .serializers import SampleSerializer
from .serializers import DropDownSerializer
from .email_helper import *
import datetime
import sys
from django.db.models import Q

# tests for views
class BaseViewTest(APITestCase):
    client = APIClient()


    def setUp(self):

        user = User.objects.create(username='testuser')
        user.set_password('12345')
        user.save()


        officer = Users.objects.create(firstname="Brian", lastname="Blake", title="Senior Chemist", user_id=user.id)
        officer.save()

        reportype = ReportTypes.objects.create(name="Standard")
        reportype.save()

        reportype2 = ReportTypes.objects.create(name="Template")
        reportype2.save()

        location = Locations.objects.create(name="Marrickville, NSW")
        location.save()

        company = CompanyDetail.objects.create(name="Enzyme Laboratories Pty Ltd",
                                               phone="02 8507 0725",
                                               web="www.enzymelabs.com.au",
                                               email="team@enzymelabs.com.au",
                                               address1="U15/168-180 Victoria Rd",
                                               address2="",
                                               city="Marrickville",
                                               state="NSW",
                                               postcode="2204",
                                               country="Australia")
        company.save()

        client = Clients.objects.create(name="Test Client",
                                        address1="12 Smart Way",
                                        city="Sydney",
                                        postcode="2000",
                                        state="NSW",
                                        country="Australia")

        client2 = Clients.objects.create(name="Test Client 2",
                                        address1="12 Smart Way",
                                        city="Sydney",
                                        postcode="2000",
                                        state="NSW",
                                        country="Australia")
        client2.save()

        #create some contacts for the client
        contact = Contacts.objects.create(firstname="Matt", lastname="Baileu", email="matt@enzymelabs.com.au", client_id=client.id)
        contact2 = Contacts.objects.create(firstname="Brian", lastname="Blake", email="brian@enzymelabs.com.au",
                                          client_id=client.id)
        contact3 = Contacts.objects.create(firstname="Tom", lastname="Blake", email="team@enzymelabs.com.au",
                                           client_id=client2.id)

        #create some notifcation groups
        ng = NotificationGroups.objects.create(name="Linked1", client_id=client.id)
        ng.contacts.set([contact, contact2])

        ng2 = NotificationGroups.objects.create(name="Default", client_id=client2.id)
        ng2.contacts.set([contact3])

        ng3 = NotificationGroups.objects.create(name="Linked2", client_id=client.id)
        ng3.contacts.set([contact])

        sg = StorageCategory.objects.create(category="Room Temp.")

        #add test methods
        tm1 = TestMethods.objects.create(name="Cellulase Activity",
                                       tmnumber="45",
                                       decimalplaces=1,
                                       error=5.0,
                                       errortype=1,
                                       description="cellualse",
                                       reporttype_id=reportype.id)
        tm1.save()

        tm2 = TestMethods.objects.create(name="Protease Activity",
                                         tmnumber="44",
                                         decimalplaces=2,
                                         error=5.0,
                                         errortype=2,
                                         description="prot",
                                         reporttype_id=reportype.id)
        tm2.save()

        # add samples
        samples = []
        for i in range(30):
            samples.append(Sample.objects.create(name="Test %d" % i,
                              received=datetime.datetime.now().date(),
                              clientref="clientref%d" % i,
                              batch="batch%d" % i,
                              condition="condition%d" % i,
                              description="desc%d" % i,
                              client_id=client.id,
                              notificationgroup_id=ng.id,
                              notified=False,
                              storage_id=sg.id))

        for i in range(3):
            samples.append(Sample.objects.create(name="Test %d" % i,
                              received=datetime.datetime.now().date(),
                              clientref="clientref%d" % i,
                              batch="batch%d" % i,
                              condition="condition%d" % i,
                              description="desc%d" % i,
                              client_id=client2.id,
                              notificationgroup_id=ng2.id,
                              notified=False,
                              storage_id=sg.id))

        #add a job
        job = Job.objects.create(ponumber="234243",
                                 client_id=client.id,
                                 notificationgroup_id=ng.id)

        #add samples to the job
        js1 = JobSample.objects.create(sample_id=samples[0].id)
        js2 = JobSample.objects.create(sample_id=samples[1].id)
        js1.save()
        js2.save()
        job.jobsamples.add(js1)
        job.jobsamples.add(js2)
        job.save()


        #add tests to the samples
        test1 = SampleTests.objects.create(jobsample_id=js1.id, location_id=location.id, officer_id=officer.id, test_id=tm1.id, testresult="45000",
                                           testunits="CU/g", testdate="22/01/2020")
        test1.save()
        test2 = SampleTests.objects.create(jobsample_id=js1.id, location_id=location.id, officer_id=officer.id, test_id=tm2.id, testresult="None Detected",
                                           testunits="PU/g", testdate="25/01/2020")
        test2.save()
        test3 = SampleTests.objects.create(jobsample_id=js2.id, location_id=location.id, officer_id=officer.id, test_id=tm2.id, testresult="22000",
                                           testunits="PU/g", testdate="25/01/2020")
        test3.save()


        #add a template report
        report_template = ReportTemplates.objects.create(name="Test Template", document="report_templates/Template.docx", report_type_id=reportype2.id)
        report_template.save()
        #add data for a custom report
        job_data = JobData.objects.create(name="Data", job_id=job.id, filepath="./eldashboard/job_data/Data.xlsx", docno=1)
        job_data.save()



        self.jobid = job.id
        self.reporttypeid = reportype.id
        self.testids = [test1.id, test2.id, test3.id]


    def login(self):
        a = self.client.login(username='testuser', password='12345')

class ManageReport(BaseViewTest):



    def test_download_report_no_login(self):
        # request a report
        response = self.client.get(reverse('downloadreport'),
                                   {"reportid": 1},
                                   format='json')
        d = response.json()
        self.assertEqual(d, {'error': 'forbidden'})

    def test_download_report_wrongid(self):
        self.login()

        # request a report
        response = self.client.get(reverse('downloadreport'),
                                   {"reportid": 99},
                                   format='json')

        d = response.json()

        self.assertEqual(d, {'error': 'Report record not found'})

    def test_download_report_file_missing(self):
        self.login()
        # create a report entry with an file that doesn't exist
        report = JobReports.objects.create(job_id=self.jobid, name="Dummy", reportno=1, filepath="./reports/doesntexist.pdf")
        report.save()

        response = self.client.get(reverse('downloadreport'),
                                   {"reportid": report.id},
                                   format='json')
        d = response.json()
        self.assertEquals(d, {'error': 'Report file not found'})

    def test_download_report_success(self):
        self.login()

        # create a report to download
        response = self.client.get(reverse('generatereport'),
                                   {"jobid": self.jobid, "reporttypeid": self.reporttypeid, "testids": self.testids},
                                   format='json')

        d = response.json()
        report = d["data"][0]

        response = self.client.get(reverse('downloadreport'),
                                   {"reportid": report["id"]},
                                   format='json')

        self.assertEquals(
            response.get('Content-Disposition'),
            'attachment; filename="Test Report_{}_{}.pdf"'.format(self.jobid, report["reportno"])
        )

    def test_email_report_no_login(self):
        # request a report
        response = self.client.get(reverse('emailreport'),
                                   {"reportid": 1},
                                   format='json')
        d = response.json()
        self.assertEqual(d, {'error': 'forbidden'})

    def test_email_report_wrongid(self):
        self.login()

        # request a report
        response = self.client.get(reverse('emailreport'),
                                   {"reportid": 99},
                                   format='json')

        d = response.json()

        self.assertEqual(d, {'error': 'Report record not found'})

    def test_email_report_file_missing(self):
        self.login()
        # create a report entry with an file that doesn't exist
        report = JobReports.objects.create(job_id=self.jobid, name="Dummy", reportno=1,
                                           filepath="./reports/doesntexist.pdf")
        report.save()

        response = self.client.get(reverse('emailreport'),
                                   {"reportid": report.id},
                                   format='json')
        d = response.json()
        self.assertEquals(d, {'error': 'Report file not found'})

    def test_email_report_success(self):
        self.login()

        # create a report to download
        response = self.client.get(reverse('generatereport'),
                                   {"jobid": self.jobid, "reporttypeid": self.reporttypeid, "testids": self.testids},
                                   format='json')

        d = response.json()
        reportid = d["data"][0]["id"]

        response = self.client.get(reverse('emailreport'),
                                   {"reportid": reportid},
                                   format='json')

        d = response.json()

        self.assertEqual(d, {'success': True})



    def test_delete_report(self):
        self.login()

        #create a report to delete
        response = self.client.get(reverse('generatereport'),
                                   {"jobid": self.jobid, "reporttypeid": self.reporttypeid, "testids": self.testids},
                                   format='json')

        d = response.json()


        reportid = d["data"][0]["id"]

        response = self.client.get(reverse('deletereport'),
                                   {"reportid": reportid},
                                   format='json')

        d = response.json()

        self.assertEqual("success" in d, True)

    def test_delete_report_missing(self):
        self.login()

        response = self.client.get(reverse('deletereport'),
                                   {"reportid": 5652},
                                   format='json')

        d = response.json()

        self.assertEqual(d, {'error': 'Report record not found'})

class EmailTester(BaseViewTest):

    def test_send_notification(self):
        self.login()

        response = self.client.get(reverse('sendnotif'),
                                   format='json')

        d = response.json()

        self.assertEqual(d['emailDetails'][0]['emails'][0][0], "matt@enzymelabs.com.au")
        self.assertEqual(d['emailDetails'][0]['emails'][1][0], "brian@enzymelabs.com.au")
        self.assertEqual(len(d['emailDetails'][0]['emails']), 2)
        self.assertEqual(d['emailDetails'][0]['sample_count'], 30)

        self.assertEqual(d['emailDetails'][1]['emails'][0][0], "team@enzymelabs.com.au")
        self.assertEqual(len(d['emailDetails'][1]['emails']), 1)
        self.assertEqual(d['emailDetails'][1]['sample_count'], 3)


    def test_send_email_attachement_success(self):
        self.login()
        # create a report to generate a odf to send
        response = self.client.get(reverse('generatereport'),
                                   {"jobid": self.jobid, "reporttypeid": self.reporttypeid, "testids": self.testids},
                                   format='json')

        d = response.json()
        filepath = d["data"][0]["filepath"]
        filename = filepath.split("/")[-1]

        fs = FileSystemStorage()
        filetype = 'application/pdf'
        file = fs.open(filepath, 'rb').read()

        success, error = send_email("matt@enzymelabs.com.au", "team@enzymelabs.com.au", "test email",
                                    "<b>Sent email HTML!</b>", "Sent Email Plain", [(file, filename, filetype)])
        self.assertEqual(success, True)

    def test_send_email_success(self):

        success, error = send_email("matt@enzymelabs.com.au", "team@enzymelabs.com.au", "test email", "<b>Sent email HTML!</b>", "Sent Email Plain")
        self.assertEqual(success, True)


class GenerateReport(BaseViewTest):

    def test_a(self):

        self.login()
        response = self.client.get('/template/1', follow=True)



    def test_generate_custom_report(self):
        self.login()
        response = self.client.get(reverse('generatecustomreport'), {"reporttemplateid": 1, "reportdataid": 1, "jobid": self.jobid}, format='json')
        d = response.json()

        self.assertEqual(d["success"], True)


    def test_generate_standard_report_miss_jobid(self):
        self.login()
        response = self.client.get(reverse('generatereport'), {"reporttypeid": 1, "sampleids":[1,4]}, format='json')
        d = response.json()
        self.assertEqual("Job" in d["errors"][0], True)

    def test_generate_standard_report_miss_reportid(self):
        self.login()
        response = self.client.get(reverse('generatereport'), {"jobid": 1, "sampleids": [3, 4]}, format='json')
        d = response.json()
        self.assertEqual("ReportType" in d["errors"][0], True)

    def test_generate_standard_report_miss_sampleid(self):
        self.login()
        response = self.client.get(reverse('generatereport'), {"jobid": 1, "reporttypeid": 1}, format='json')
        d = response.json()
        self.assertEqual("Test" in d["errors"][0], True)

    def test_generate_standard_report_miss_multiple(self):
        self.login()
        response = self.client.get(reverse('generatereport'), format='json')
        d = response.json()
        self.assertEqual(len(d["errors"]), 3)

    def test_generate_standard_report_multiple(self):
        self.login()
        response = self.client.get(reverse('generatereport'), {"jobid": self.jobid, "reporttypeid": self.reporttypeid, "testids":self.testids}, format='json')
        d = response.json()
        self.assertEqual("errors" not in d, True)
        response = self.client.get(reverse('generatereport'), {"jobid": self.jobid, "reporttypeid": self.reporttypeid, "testids": [self.testids[1]]},
                                   format='json')
        d = response.json()
        self.assertEqual("errors" not in d, True)
        response = self.client.get(reverse('generatereport'), {"jobid": self.jobid, "reporttypeid": self.reporttypeid, "testids": [self.testids[0]]},
                                   format='json')
        d = response.json()
        self.assertEqual("errors" not in d, True)

    def test_generate_standard_report_one_sample(self):
        self.login()
        response = self.client.get(reverse('generatereport'), {"jobid": self.jobid, "reporttypeid": self.reporttypeid, "testids":self.testids[2]}, format='json')
        d = response.json()
        self.assertEqual("errors" not in d, True)

class GetSamplesTest(BaseViewTest):

    def test_get_linked_notify_groups(self):
        """
        This test ensures that notification groups attached to the client id are returned
        """
        self.login()

        client = Clients.objects.first()
        ng = NotificationGroups.objects.first()

        # hit the API endpoint
        response = self.client.get(reverse('linkednotifcationgroups'), {"client_id": client.id}, format='json')

        expected = NotificationGroups.objects.filter(contacts__client_id=client.id)

        # format queryset into json for returning
        serializer = DropDownSerializer(expected, many=True)

        response_item_count = len(response.json())
        #sys.stderr.write(repr(len(response.json())) + '\n')


        self.assertEqual(response_item_count, 2) #should only be 2 linked notification groups
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_samples(self):

        """
        This test ensures that all samples added in the setUp method
        exist when loop through the pages in the sample list
        """
        self.login()

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
        self.login()

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

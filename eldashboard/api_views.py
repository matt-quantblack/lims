import base64
import os
from email.mime.text import MIMEText

from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from django.db.models import Q
from django.db.models import Max
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .static_report_standard import generate_report as generate_static_standard_report
from .models import *
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse

from .serializers import *
from .email_helper import send_email
from django.shortcuts import redirect

from django.db.models.functions import Cast
from django.db.models import CharField

import datetime

def is_float(n):
    try:
        float(n)
        return True
    except:
        return False

def generatereport(request):

    if request.user.is_authenticated == False:
        return JsonResponse({'errors': ['forbidden']})

    #get the request parameters and ensure all is valid
    jobid = request.GET.get('jobid', None)
    reporttypeid = request.GET.get('reporttypeid', None)
    reportname = request.GET.get('reportname', 'Test Report')
    testlist = {int(x) for x in request.GET.getlist('testids', None)}

    errors = []
    if jobid is None:
        errors.append("JobId missing from request.")
    if reporttypeid is None:
        errors.append("ReportTypeId missing from request.")
    if testlist is None or len(testlist) == 0:
        errors.append("Test ids are missing from request")

    if len(errors) > 0:
        return JsonResponse({'errors': errors})

    #get the database data
    company = CompanyDetail.objects.first()

    if company is None:
        errors.append("No default Company in database.")

    job = Job.objects.get(id=jobid)

    if job is None:
        errors.append("Job number does not exist.")

    officer = Users.objects.get(user_id=request.user.id)

    if officer is None:
        errors.append("This officer doesn't exist.")

    #get the report number count
    reportno = 1
    maxno = JobReports.objects.filter(job_id=jobid).aggregate(Max('reportno'))
    if maxno["reportno__max"] is not None:
        reportno = maxno["reportno__max"]+1

    if len(errors) > 0:
        return JsonResponse({'errors': errors})

    #format the data for the report
    header_fields = {
        'TestOfficer': '{} {}'.format(officer.firstname, officer.lastname),
        'Title': officer.title,
        'Company_Phone': company.phone,
        'Company_Email': company.email,
        'Company_Web': company.web,
        'Company_Address1': '{} {}'.format(company.address1, company.address2),
        'Company_Address2': '{} | {} | {} | {}'.format(company.city, company.state, company.postcode, company.country),
        'Job_Id': '{} - {}'.format(job.id, reportno),
        'Now': datetime.date.today().strftime("%d/%m/%Y"),
        'Sample_Client_Name': job.client.name,
        'Sample_Client_Full_Address': '{} {} {} {} {} {}'.format(job.client.address1, job.client.address2,
                                                                     job.client.city, job.client.postcode,
                                                                     job.client.state, job.client.country),
    }

    samples = []
    for jobsample in job.jobsamples.all():

        fields = {
            'Sample_Name': jobsample.sample.name,
            'Sample_ClientRef': jobsample.sample.clientref,
            'Sample_Batch': jobsample.sample.batch,
            'Sample_Id': jobsample.sample.id,
            'Sample_Condition': jobsample.sample.condition,
            'Sample_Description': jobsample.sample.description,
            'Sample_Received': jobsample.sample.received.strftime("%d/%m/%Y"),
        }


        #get tests related to this jobsample
        tests = SampleTests.objects.filter(jobsample_id=jobsample.id)

        #build the data from these tests
        table_data = []
        for test in tests:

            dp = test.test.decimalplaces
            if dp == 0:
                dp = None

            if test.id in testlist:

                #calc error
                error = ""
                if is_float(test.testresult):

                    test.testresult = round(float(test.testresult), dp)

                    error = '(+-) {val:,}'.format(val=round(test.test.error, dp))
                    if test.test.errortype == 1: #relative error
                        val = round(float(test.testresult), dp)
                        error = '(+-) {val:,}'.format(val=round(val * test.test.error / 100, dp))

                table_data.append({
                    'Method': 'TM{} {}'.format(test.test.tmnumber, test.test.name),
                    'Result': '{val1:,} {val2:}'.format(val1=test.testresult, val2=error),
                    'Units': test.testunits,
                    'Details': 'Tested on: {}\nTesting Officer: {} {}\nLocation: {}'.format(test.testdate,
                                                   officer.firstname, officer.lastname,
                                                   test.location.name)})

        if len(table_data) > 0:
            #add this sample to the data
            samples.append({
                "fields": fields,
                "tests": table_data
            })

    data = {
        'header_fields': header_fields,
        'samples': samples}

    #try to generate the report and save it
    filepath = "./eldashboard/reports/Test_Report_{}_{}.pdf".format(jobid, reportno)
    try:
        generate_static_standard_report(data, filepath)
    except (KeyError, ValueError, FileNotFoundError) as e:
        return JsonResponse({'errors':['Report generation failed {}'.format(e)]})

    # create a db entry
    report = JobReports.objects.create(job_id=jobid, name=reportname, filepath=filepath, reportno=reportno)
    report.save()

    context = {
        'data': [JobReportSerializer(report).data],
        'more': False
    }

    return JsonResponse(context)

def getreportfromrequestid(request):

    if request.user.is_authenticated == False:
        return None,  JsonResponse({'error': 'forbidden'})

    #get the client id from the request and convert to an int
    reportid = request.GET.get('reportid', None)

    #get the report
    try:
        report = JobReports.objects.get(id=reportid)
    except JobReports.DoesNotExist:
        return None, JsonResponse({'error': 'Report record not found'})

    return report, None


def deletereport(request):

    report, response = getreportfromrequestid(request)
    if response is not None:
        return response

    #try to delete the file
    try:
        fs = FileSystemStorage()
        fs.delete(report.filepath)
    except IOError as e:
        print(e)

    #delete record from db
    report.delete()

    return JsonResponse({'success': True})

def downloadreport(request):

    report, response = getreportfromrequestid(request)
    if response is not None:
        return response

    try:
        fs = FileSystemStorage()
        response = FileResponse(fs.open(report.filepath, 'rb'), content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename="{}_{}_{}.pdf"'.format(report.name, report.job_id,
                                                                                       report.reportno)
    except FileNotFoundError:
        return JsonResponse({'error': 'Report file not found'})

    return response

def emailreport(request):

    report, response = getreportfromrequestid(request)
    if response is not None:
        return response

    try:
        fs = FileSystemStorage()
        file = fs.open(report.filepath, 'rb').read()

    except FileNotFoundError:
        return JsonResponse({'error': 'Report file not found'})

    filename = report.filepath.split("/")[-1]
    filetype = "application/pdf"

    emails = []
    contacts = report.job.notificationgroup.contacts.all()
    for contact in contacts:
        emails.append((contact.email, '{} {}'.format(contact.firstname, contact.lastname)))

    companyname = report.job.client.name

    emailtext = """Hi {},
    
    Your test reports from Enzyme Labs are complete.
    
    Please find test reports attached.
    
    Don't hesitate to contact us if you have any questions.
    
    Best Regards,
    The Enzyme Labs Team
    
    U15/168 Victoria Rd
    Marrickville
    NSW 2204
    Australia""".format(companyname)

    success, error = send_email(emails, ("team@enzymelabs.com.au", "Enzyme Labs"), "Test Report from Enzyme Labs",
                                emailtext.replace("\n", "<br/>"),
                                emailtext,
                                attachments=[(file, filename, filetype)],
                                bcc="info@enzymelabs.com.au")

    if success:
        #save the new job status
        job = Job.objects.get(id=report.job_id)
        job.status = "Sent"
        job.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'error': 'Failed to send email: {}'.format(error)})

def uploadreport(request):


    reportname = request.POST.get('reportname', 'Test Report')
    jobid = int(request.POST.get('jobid', None))
    upfile = request.FILES.get('file', None)

    if upfile is None:
        return JsonResponse({'error': 'Report file needs to be submitted.'})

    if request.method == 'POST':

        try:
            # get the report number count
            reportno = 1
            maxno = JobReports.objects.filter(job_id=jobid).aggregate(Max('reportno'))
            if maxno["reportno__max"] is not None:
                reportno = maxno["reportno__max"] + 1

            fs = FileSystemStorage()
            filepath = './eldashboard/reports/{}_{}_{}.pdf'.format(reportname, jobid, reportno)

            fs.save(filepath, upfile)

            report = JobReports.objects.create(job_id=jobid, name=reportname, filepath=filepath, reportno=reportno)
            report.save()

        except Exception as e:
            return JsonResponse({'error': 'Could not save file {}'.format(e)})

        context = {
            'data': [JobReportSerializer(report).data],
            'more': False
        }

        return JsonResponse(context)

    return JsonResponse({'error': 'Wrong method, use POST.'})

def markinvoiced(request):
    if request.user.is_authenticated == False:
        return JsonResponse({'error': 'forbidden'})

    #get the client id from the request and convert to an int
    jobid = request.GET.get('jobid', None)
    invoiceno = request.GET.get('invoice', 'Not provided')

    try:
        job = Job.objects.get(id=jobid)
        job.invoiceno = invoiceno
        job.status = "Complete"
        job.save()

    except Exception as e:
        return JsonResponse({'success': False, 'error': 'Could not delete {}'.format(e)})

    return JsonResponse({'success': True})

def linkednotifcationgroups(request):

    if request.user.is_authenticated == False:
        return JsonResponse({'error': 'forbidden'})

    #get the client id from the request and convert to an int
    client_id = request.GET.get('client_id', None)
    if client_id is not None and client_id.isnumeric():
        client_id = int(client_id)
    else:
        client_id = -1

    results = NotificationGroups.objects.filter(client_id=client_id)

    # format queryset into json for returning
    serializer = DropDownSerializer(results, many=True)

    return JsonResponse(serializer.data, safe=False)

def removenotif(request):

    if request.user.is_authenticated == False:
        return JsonResponse({'error': 'forbidden'})

    try:
        #get the id from the request and convert to an int
        id = int(request.GET.get('id', None))

        #update the sample
        sample = Sample.objects.get(id=id)
        sample.notified = True
        sample.save()
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'Could not delete {}'.format(e)})

    return JsonResponse({'success': True})

def sendnotif(request):

    if request.user.is_authenticated == False:
        return JsonResponse({'error': 'forbidden'})

    newsamples = Sample.objects.filter(notified=False).all()

    emailsToSend = {}

    #first compile a list of all the samples for each contact
    #(may be multiple samples to same contact so want only one email"
    for sample in newsamples:
        sample.notified = True
        sample.save()

        emails = []
        for contact in sample.notificationgroup.contacts.all():
            if contact.id not in emailsToSend:
                emailsToSend[contact.id] = {'contact': contact, 'samples': []}

            emailsToSend[contact.id]['samples'].append(sample)

    errors = ""
    for id in emailsToSend:
        info = emailsToSend[id]
        contact = info['contact']
        emails.append((contact.email, '{} {}'.format(contact.firstname, contact.lastname)))

        emailtext = """Hi {},
    
            The following samples have been received by Enzyme Labs: \n\n""".format(contact.firstname)

        for sample in info['samples']:
            emailtext += "#{} - Name:{}, Batch:{}, ClientRef: {}\n".format(sample.id,
                                                                         sample.name,
                                                                         sample.batch,
                                                                         sample.clientref)

        emailtext += """
    
            If there are any issues please don't hesitate to contact us.
    
            Best Regards,
            The Enzyme Labs Team
            
            U15/168 Victoria Rd
            Marrickville
            NSW 2204
            Australia"""

        success, error = send_email(emails, ("team@enzymelabs.com.au", "Enzyme Labs"), "Sample Received from Enzyme Labs",
                                    emailtext.replace("\n", "<br/>"),
                                    emailtext,
                                    bcc="info@enzymelabs.com.au")
        if success == False:
            errors += "{}: {},".format(contact.email, error)



        if len(errors) > 0:
            return JsonResponse({'success': False, 'error': 'Could not send: {}'.format(errors)})

    return JsonResponse({'success': True})

def addng(request):

    if request.user.is_authenticated == False:
        return JsonResponse({'error': 'forbidden'})

    name = request.GET.get('name', None)
    clientid = int(request.GET.get('clientid', None))

    ng = NotificationGroups.objects.create(name=name, client_id=clientid)
    ng.save()

    context = {
        'data': [NotificationGroupSerializer(ng).data],
        'more': False
    }

    return JsonResponse(context)


def removeng(request):
    if request.user.is_authenticated == False:
        return JsonResponse({'error': 'forbidden'})

    ngid = int(request.GET.get('ngid', None))

    try:
        ng = NotificationGroups.objects.get(id=ngid)
        ng.delete()
    except Exception as e:
        return JsonResponse({'success': False ,'error': 'Could not delete {}'.format(e)})

    return JsonResponse({'success': True})

def addcontacts(request):
    if request.user.is_authenticated == False:
        return JsonResponse({'error': 'forbidden'})

    ng_id = request.GET.get('refid', None)
    contact_ids = request.GET.get('ids', None)

    if ng_id.isnumeric():

        #get the ng id as an int
        ng_id = int(ng_id)

        #get the sample ids as a list
        selected = contact_ids.split(',')

        #get the current job list of jobsamples
        #because we needs to sync current job samples with the posted sample ids
        ng = NotificationGroups.objects.get(id=ng_id)
        currentcontacts = ng.contacts.all()

        #make a list of current ids to make it easier to check in the next loop
        currentids = []
        for s in currentcontacts:
            currentids.append(s.id)

        #go through each id that was posted and add it to the job only if it isn't already in the job
        for id in selected:
            if id.isnumeric():
                id = int(id)

                #only add if not in the job
                if id not in currentids:
                    contact = Contacts.objects.get(id=id)
                    ng.contacts.add(contact)

        #now delete any from the job that weren't in the posted list of ids
        for s in currentcontacts:
            if str(s.id) not in selected:
                ng.contacts.remove(s)

        #save the job to save the relationship of jobsamples and job in the job_jobsamples table
        ng.save()


    else:
        return JsonResponse({'success': False, 'error': 'Id not valid number.'})

    return JsonResponse({'success': True})


def addsamples(request):
    if request.user.is_authenticated == False:
        return JsonResponse({'error': 'forbidden'})

    job_id = request.GET.get('refid', None)
    sample_ids = request.GET.get('ids', None)

    if job_id.isnumeric():

        #get the job id as an int
        job_id = int(job_id)

        #get the sample ids as a list
        selected = sample_ids.split(',')

        #get the current job list of jobsamples
        #because we needs to sync current job samples with the posted sample ids
        job = Job.objects.get(id=job_id)
        currentsamples = job.jobsamples.all()

        #make a list of current sample ids to make it easier to check in the next loop
        currentids = []
        for s in currentsamples:
            currentids.append(s.sample.id)

        #go through each sample id that was posted and add it to the job only if it isn't already in the job
        for id in selected:
            if id.isnumeric():
                id = int(id)

                #only add if not in the job
                if id not in currentids:
                    jobsample = JobSample()
                    jobsample.sample_id = id
                    jobsample.save()

                    job.jobsamples.add(jobsample)

        #now delete any samples from the job that weren't in the posted list of sample ids
        for s in currentsamples:
            if str(s.sample.id) not in selected:
                job.jobsamples.remove(s)
                #make sure to delete the associated records in the tests and jobs tables
                SampleTests.objects.filter(jobsample_id=s.id).delete()
                JobSample.objects.get(id=s.id).delete()


        #save the job to save the relationship of jobsamples and job in the job_jobsamples table
        job.save()


    else:
        return JsonResponse({'success': False, 'error': 'Job id not valid number.'})

    return JsonResponse({'success': True})

def deleteresult(request):
    if request.user.is_authenticated == False:
        return JsonResponse({'error': 'forbidden'})

    id = request.GET.get('id', None)
    SampleTests.objects.get(id=id).delete()
    return JsonResponse({'success': True})

def saveresults(request):
    if request.user.is_authenticated == False:
        return JsonResponse({'error': 'forbidden'})

    id = request.GET.get('id', None)
    testdate = request.GET.get('testdate', None)
    value = request.GET.get('value', None)
    units = request.GET.get('units', None)
    officer = request.GET.get('officer', None)
    location = request.GET.get('location', None)

    item = SampleTests.objects.get(id=id)
    item.testdate = testdate
    item.testresult = value
    item.testunits = units
    item.officer_id = officer
    item.location_id = location

    item.save()

    return JsonResponse({'success': True})

def assignsamples(request):
    if request.user.is_authenticated == False:
        return JsonResponse({'error': 'forbidden'})


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
    if request.user.is_authenticated == False:
        return JsonResponse({'error': 'forbidden'})


    query = request.GET.get('q')
    page_size = request.GET.get('page_size', 20)
    page = request.GET.get('page')

    if query:
        results = Sample.objects.filter(Q(id__icontains=query) | \
                                        Q(clientref__icontains=query) | \
                                        Q(name__icontains=query) | \
                                        Q(client__name__icontains=query) | \
                                        Q(batch__icontains=query)).distinct().order_by("-received")
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
    if request.user.is_authenticated == False:
        return JsonResponse({'error': 'forbidden'})

    query = request.GET.get('q')
    page_size = request.GET.get('page_size', 20)
    page = request.GET.get('page')

    if query:
        results = Job.objects.annotate(id_str=Cast('jobsamples__sample_id', output_field=CharField()),).\
            filter(Q(id__icontains=query) |\
                   Q(client__name__icontains=query) |\
                   Q(id_str__icontains=query) |\
                   Q(jobsamples__sample__name__icontains=query)).distinct().order_by("-id")

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
    if request.user.is_authenticated == False:
        return JsonResponse({'error': 'forbidden'})

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
    if request.user.is_authenticated == False:
        return JsonResponse({'error': 'forbidden'})

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
    if request.user.is_authenticated == False:
        return JsonResponse({'error': 'forbidden'})

    clientid = request.GET.get('refid')
    query = request.GET.get('q')
    page_size = request.GET.get('page_size', 20)
    page = request.GET.get('page')

    print(query)
    if query:
        results = Contacts.objects.filter(Q(client=clientid) & \
                                          (Q(firstname__icontains=query) | \
                                          Q(lastname__icontains=query) | \
                                          Q(email__icontains=query))).distinct().order_by("firstname")
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

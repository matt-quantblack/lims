from django.db import models
from django.contrib.auth.models import User
import os
from django.dispatch import receiver
from ELLIMS.storage_backends import PublicMediaStorage

class CompanyDetail(models.Model):

    name = models.CharField(max_length=50, null=False, blank=False)
    phone = models.CharField(max_length=50, null=False, blank=False)
    email = models.CharField(max_length=50, null=False, blank=False)
    web = models.CharField(max_length=50, null=False, blank=False)
    address1 = models.CharField(max_length=50, null=False, blank=False)
    address2 = models.CharField(max_length=50, null=False, blank=False)
    city = models.CharField(max_length=50, null=False, blank=False)
    state = models.CharField(max_length=50, null=False, blank=False)
    postcode = models.CharField(max_length=50, null=False, blank=False)
    country = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "companydetails"

class ReportTypes(models.Model):

    name = models.CharField(max_length=25, null=False, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "reporttypes"

class TestMethods(models.Model):

    name = models.CharField(max_length=100, null=False, blank=False)
    tmnumber = models.CharField(max_length=15, null=False, blank=False)
    decimalplaces = models.IntegerField(null=False, blank=False)
    error = models.FloatField(null=False, blank=False)
    errortype = models.IntegerField(null=False, blank=False)
    reporttype = models.ForeignKey(ReportTypes, default=1, on_delete=models.SET_DEFAULT)
    description = models.CharField(max_length=200, null=False, blank=True, default='')

    def __str__(self):
        return self.name

    class Meta:
        db_table = "testmethods"

class Clients(models.Model):

    name = models.CharField(max_length=50, null=False, blank=False)

    address1 = models.CharField(max_length=50, verbose_name="Address 1", null=False, blank=False)
    address2 = models.CharField(max_length=50, verbose_name="Address 2", null=True, blank=True, default='')
    city = models.CharField(max_length=25, null=False, blank=False)
    postcode = models.CharField(max_length=10, null=False, blank=False)
    state = models.CharField(max_length=25, null=False, blank=False)
    country = models.CharField(max_length=25, null=True, blank=True, default='')


    def __str__(self):
        return self.name

    class Meta:
        db_table = "clients"

class Contacts(models.Model):

    firstname = models.CharField(max_length=25, null=False, blank=False)
    lastname = models.CharField(max_length=25, null=False, blank=True, default='')
    email = models.CharField(max_length=50, null=False, blank=False)
    phone = models.CharField(max_length=25, null=False, blank=True, default='')
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)

    def __str__(self):
        return self.firstname + self.lastname

    class Meta:
        db_table = "contacts"

class NotificationGroups(models.Model):

    name = models.CharField(max_length=25)
    contacts = models.ManyToManyField(Contacts)
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "notificationgroups"

class StorageCategory(models.Model):

    category = models.CharField(max_length=25)

    def __str__(self):
        return self.category

    class Meta:
        db_table = "storagecategories"

class Sample(models.Model):

    name = models.CharField(max_length=100)
    clientref = models.CharField(max_length=100, default='')
    batch = models.CharField(max_length=50, null=False, blank=True, default='')
    condition = models.CharField(max_length=100, null=False, blank=True, default='')
    description = models.CharField(max_length=100, null=False, blank=True, default='')
    received = models.DateField(null=False, blank=False)
    storage = models.ForeignKey(StorageCategory, default=1, on_delete=models.SET_DEFAULT)
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    notificationgroup = models.ForeignKey(NotificationGroups, null=True, on_delete=models.SET_NULL)
    notified = models.BooleanField(default=False)

    class Meta:
        db_table = "samples"

class JobSample(models.Model):

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)

    def __str__(self):
        return self.sample.name

    class Meta:
        db_table = "jobsamples"

class Users(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=25, null=False, blank=False)
    lastname = models.CharField(max_length=25, null=False, blank=False)
    title = models.CharField(max_length=25, null=False, blank=False)

    def __str__(self):
        return "{} {}".format(self.firstname, self.lastname)

    class Meta:
        db_table = "users"

class Locations(models.Model):

    name = models.CharField(max_length=25, null=False, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "locations"

class SampleTests(models.Model):

    jobsample = models.ForeignKey(JobSample, on_delete=models.CASCADE)
    test = models.ForeignKey(TestMethods, on_delete=models.CASCADE)
    testresult = models.CharField(max_length=50, null=False, blank=True, default='')
    testunits = models.CharField(max_length=50, null=False, blank=True, default='')
    testdate = models.CharField(max_length=25, null=False, blank=True, default='')
    officer = models.ForeignKey(Users, null=True, on_delete=models.SET_NULL)
    location = models.ForeignKey(Locations, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.jobsample.sample.name

    class Meta:
        db_table = "sampletests"

class Job(models.Model):

    ponumber = models.CharField(max_length=25)
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    notificationgroup = models.ForeignKey(NotificationGroups, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=25, default="Open")
    invoiceno = models.CharField(max_length=25, default="")
    jobsamples = models.ManyToManyField(JobSample)

    def __str__(self):
        return "Job #{}".format(self.id)

    class Meta:
        db_table = "jobs"

class JobReports(models.Model):

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=False, blank=False)
    filepath = models.CharField(max_length=100, null=False, blank=False)
    reportno = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "jobreports"

class ReportTemplates(models.Model):

    name = models.CharField(max_length=50, null=False, blank=False)
    report_type = models.ForeignKey(ReportTypes, on_delete=models.CASCADE)
    document = models.FileField(storage=PublicMediaStorage())

    def __str__(self):
        return self.name

    class Meta:
        db_table = "reporttemplates"


class JobData(models.Model):

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=False, blank=False, default='')
    filepath = models.CharField(max_length=100, null=False, blank=False)
    docno = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "jobdata"

class JobActivity(models.Model):

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    details = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "jobactivity"



# These two auto-delete files from filesystem when they are unneeded:
@receiver(models.signals.post_delete, sender=ReportTemplates)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.document:
        if os.path.isfile(instance.document.path):
            os.remove(instance.document.path)

@receiver(models.signals.pre_save, sender=ReportTemplates)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = ReportTemplates.objects.get(pk=instance.pk).document
    except ReportTemplates.DoesNotExist:
        return False

    new_file = instance.document
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

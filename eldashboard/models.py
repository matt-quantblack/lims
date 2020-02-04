from django.db import models

class ReportTypes(models.Model):

    name = models.CharField(max_length=25, null=False, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "reporttypes"

class TestMethods(models.Model):

    name = models.CharField(max_length=25, null=False, blank=False)
    tmnumber = models.CharField(max_length=5, verbose_name="TM #", null=False, blank=False)
    decimalplaces = models.IntegerField(verbose_name="Decimal Places", null=False, blank=False)
    relativeError = models.FloatField(verbose_name="Relative Error %", null=False, blank=False)
    absoluteError = models.FloatField(verbose_name="Absolute Error", null=False, blank=False)
    reporttype = models.ForeignKey(ReportTypes, default=1, verbose_name="Report Types", on_delete=models.SET_DEFAULT)
    description = models.CharField(max_length=200, null=False, blank=True, default='')

    def __str__(self):
        return self.name

    class Meta:
        db_table = "testmethods"


class Clients(models.Model):

    name = models.CharField(max_length=25, null=False, blank=False)

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

    name = models.CharField(max_length=50)
    clientref = models.CharField(max_length=50, default='')
    batch = models.CharField(max_length=50, null=False, blank=True, default='')
    condition = models.CharField(max_length=50, null=False, blank=True, default='')
    description = models.CharField(max_length=100, null=False, blank=True, default='')
    received = models.DateField(null=False, blank=False)
    storage = models.ForeignKey(StorageCategory, default=1, verbose_name="Storage", on_delete=models.SET_DEFAULT)
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    notificationgroup = models.ForeignKey(NotificationGroups, null=True, on_delete=models.SET_NULL)


    class Meta:
        db_table = "samples"


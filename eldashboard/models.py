from django.db import models

class Clients(models.Model):

    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "clients"

class Contacts(models.Model):

    firstname = models.CharField(max_length=25)
    lastname = models.CharField(max_length=25)
    email = models.CharField(max_length=50)
    client = models.ForeignKey(Clients, verbose_name="Storage", on_delete=models.CASCADE)

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
    batch = models.CharField(max_length=50, default='')
    condition = models.CharField(max_length=50, default='')
    description = models.CharField(max_length=100, default='')
    received = models.DateField(null=False, blank=False)
    storage = models.ForeignKey(StorageCategory, default=1, verbose_name="Storage", on_delete=models.SET_DEFAULT)
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    notificationgroup = models.ForeignKey(NotificationGroups, null=True, on_delete=models.SET_NULL)


    class Meta:
        db_table = "samples"


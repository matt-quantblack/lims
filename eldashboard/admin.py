from django.contrib import admin

from django.contrib import admin
from .models import *

admin.site.register(Sample)
admin.site.register(Users)
admin.site.register(Locations)
admin.site.register(ReportTypes)
admin.site.register(CompanyDetail)
admin.site.register(Contacts)
admin.site.register(Job)
admin.site.register(NotificationGroups)


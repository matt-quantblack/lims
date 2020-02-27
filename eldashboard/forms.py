from django import forms
from ELLIMS import settings

from .models import Sample
from .models import Clients
from .models import Contacts
from .models import TestMethods
from .models import Job

class SampleForm(forms.ModelForm):

   #setup the datepicker input and display date formates
   received = forms.DateField(
      widget=forms.DateInput(format=settings.DATE_INPUT_FORMATS[0]),
      input_formats=(settings.DATE_INPUT_FORMATS[0],)
   )


   class Meta:
      model = Sample
      fields = ['name', 'clientref', 'batch', 'condition', 'description', 'storage', 'received', 'client', 'notificationgroup']
      labels = {
         'clientref': 'Client Ref',
         'notificationgroup': 'Notification Group'
      }


class ClientForm(forms.ModelForm):

   class Meta:
      model = Clients
      fields = '__all__'

class TestMethodForm(forms.ModelForm):

   CHOICES = (
      (0, 'N/A'),
      (1, 'Relative Error'),
      (2, 'Absolute Error')
   )

   errortype = forms.ChoiceField(choices=CHOICES, label="Error Type")

   class Meta:
      model = TestMethods
      fields = '__all__'
      labels = {
         'decimalplaces': 'Decimal Places',
         'tmnumber': 'TM #',
         'reporttype': 'Report Type'
      }

class ContactForm(forms.ModelForm):

   class Meta:
      model = Contacts
      fields = ['firstname', 'lastname', 'email', 'phone', 'client']
      widgets = {'client': forms.HiddenInput()}


class JobForm(forms.ModelForm):

   class Meta:
      model = Job
      fields = ['client', 'notificationgroup', 'ponumber']
      labels = {
         'ponumber': "PO Number",
         'notificationgroup': 'Notification Group'
      }

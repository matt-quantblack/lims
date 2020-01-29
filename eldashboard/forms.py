from django import forms
from ELLIMS import settings

from eldashboard.models import Sample

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

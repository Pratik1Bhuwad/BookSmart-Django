# appointments/forms.py
from django import forms
from .models import Appointment

class AppointmentRequestForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['client', 'provider_service', 'time_slot', 'location', 'date']

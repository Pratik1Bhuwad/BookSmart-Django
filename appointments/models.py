# appointments/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from providers.models import ProviderService, ProviderTimeSlot, ServiceLocation

User = get_user_model()

class Appointment(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    provider_service = models.ForeignKey(ProviderService, on_delete=models.CASCADE, related_name='appointments')
    time_slot = models.ForeignKey(ProviderTimeSlot, on_delete=models.CASCADE, related_name='appointments')
    location = models.ForeignKey(ServiceLocation, on_delete=models.SET_NULL, null=True, related_name='appointments')
    date = models.DateField()
    booked_on = models.DateTimeField(auto_now_add=True)
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
        ('completed', 'Completed'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"Appointment for {self.provider_service.name} with {self.client.username}"

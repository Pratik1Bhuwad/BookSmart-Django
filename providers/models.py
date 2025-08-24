# providers/models.py
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from services.models import ServiceSubCategory

User = get_user_model()

class ServiceProvider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='service_provider_profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True, help_text="City or address of the provider.")

    def __str__(self):
        return self.user.username

class ServiceLocation(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="e.g., 'Mumbai', 'Online', 'Goa'")

    def __str__(self):
        return self.name

class ProviderService(models.Model):
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='provider_details')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='service_offerings')
    sub_category = models.ForeignKey(ServiceSubCategory, on_delete=models.CASCADE, related_name='provider_services')
    name = models.CharField(max_length=255, help_text="e.g., 'Basic Facial', 'Anti-Aging Facial'")
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField(help_text="Duration in minutes")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='provider_service_images/')
    locations = models.ManyToManyField(ServiceLocation, related_name='providers')

    def __str__(self):
        return f"{self.name} by {self.provider.user.username}"

class ProviderTimeSlot(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='time_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['provider', 'date', 'start_time', 'end_time'],
                name='unique_provider_time_slot'
            )
        ]

    def __str__(self):
        return f"{self.provider.user.username} on {self.date} from {self.start_time} to {self.end_time}"
      
class WorkingHours(models.Model):
    DAY_OF_WEEK_CHOICES = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'),
        (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ]
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='working_hours')
    day_of_week = models.IntegerField(choices=DAY_OF_WEEK_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('provider', 'day_of_week')
        ordering = ['day_of_week', 'start_time']
        verbose_name_plural = "Working Hours"

    def __str__(self):
        return f"{self.provider.user.username}'s {self.get_day_of_week_display()} ({self.start_time}-{self.end_time})"

class BlockedSlot(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='blocked_slots', null=True, blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    reason = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['provider', 'date', 'start_time', 'end_time'],
                name='unique_provider_blocked_slot_per_day'
            )
        ]
        ordering = ['date', 'start_time']

    def __str__(self):
        if self.provider:
            return f"Blocked by {self.provider.user.username}: {self.date} {self.start_time}-{self.end_time}"
        return f"General Block: {self.date} {self.start_time}-{self.end_time}"

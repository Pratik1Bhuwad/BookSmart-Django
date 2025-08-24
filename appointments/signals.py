# appointments/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Appointment
from providers.models import ProviderService, ServiceProvider # Correct imports

@receiver(post_save, sender=Appointment)
def send_booking_confirmation_email(sender, instance, created, **kwargs):
    """
    Sends an email and SMS confirmation when a new appointment is created.
    """
    # Only send on initial creation of the appointment
    if created:
        subject = f'Appointment Confirmation: {instance.provider_service.name} with {instance.provider_service.provider.user.username}'
        message = f"Hello {instance.client.username},\n\nYour appointment has been successfully booked.\n"
        html_message = render_to_string('appointments/email_notification.html', {'appointment': instance})
        
        # Send email confirmation
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.client.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Placeholder for SMS notification logic
        # You would use an SMS library like Twilio here.
        # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        # client.messages.create(
        #     body=f"Hi {instance.user.username}, your appointment for {instance.service.name} is booked.",
        #     from_=settings.TWILIO_PHONE_NUMBER,
        #     to=instance.provider.phone_number
        # )

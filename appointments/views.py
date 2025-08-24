# appointments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment
from providers.models import ProviderService, ProviderTimeSlot, ServiceLocation
from services.models import ServiceCategory, ServiceSubCategory
from .forms import AppointmentRequestForm
from django.conf import settings # NEW: Import settings

@login_required
def home_page(request):
    categories = ServiceCategory.objects.all()
    return render(request, 'appointments/home.html', {'categories': categories})

@login_required
def select_subcategory(request, category_id):
    category = get_object_or_404(ServiceCategory, id=category_id)
    subcategories = category.subcategories.all()
    return render(request, 'appointments/select_subcategory.html', {'category': category, 'subcategories': subcategories})

@login_required
def select_provider_service(request, subcategory_id):
    subcategory = get_object_or_404(ServiceSubCategory, id=subcategory_id)
    provider_services = ProviderService.objects.filter(sub_category=subcategory)
    locations = ServiceLocation.objects.all()
    return render(request, 'appointments/select_provider_service.html', {'subcategory': subcategory, 'provider_services': provider_services, 'locations': locations})

@login_required
def appointment_request(request, provider_service_id):
    provider_service = get_object_or_404(ProviderService, id=provider_service_id)
    if request.method == 'POST':
        form = AppointmentRequestForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.client = request.user
            appointment.save()
            messages.success(request, 'Appointment request sent successfully!')
            return redirect('client_appointments')
    else:
        form = AppointmentRequestForm(initial={'provider_service': provider_service})
    
    return render(request, 'appointments/appointment_request.html', {'form': form, 'provider_service': provider_service})

@login_required
def client_appointments(request):
    appointments = Appointment.objects.filter(client=request.user)
    
    context = {
        'appointments': appointments,
        'settings': settings, # NEW: Pass settings to the template
    }
    return render(request, 'appointments/client_appointments.html', context)

# providers/views.py
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import ServiceProvider, ProviderService, ProviderTimeSlot, ServiceLocation, WorkingHours, BlockedSlot
from services.models import ServiceCategory, ServiceSubCategory, Service
from appointments.models import Appointment
from .forms import ProviderServiceForm, ProviderTimeSlotForm, WorkingHoursForm, ProviderBlockedSlotForm
from django.http import JsonResponse
from django.db.models import F
from datetime import datetime, timedelta, date
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.db.models import Q

def is_service_provider(user):
    return hasattr(user, 'service_provider_profile')

# Initialize Stripe with the secret key from settings
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
@user_passes_test(is_service_provider, login_url='/accounts/login/')
def provider_dashboard(request):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    provider_services = ProviderService.objects.filter(provider=provider)
    pending_appointments = Appointment.objects.filter(provider_service__provider=provider, status='pending')
    
    context = {
        'provider': provider,
        'provider_services': provider_services,
        'pending_appointments': pending_appointments,
    }
    return render(request, 'providers/dashboard.html', context)


@login_required
@user_passes_test(is_service_provider, login_url='/accounts/login/')
def manage_provider_services(request):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    provider_services = ProviderService.objects.filter(provider=provider)
    
    if request.method == 'POST':
        if 'delete_service' in request.POST:
            ps_id = request.POST.get('ps_id')
            ps = get_object_or_404(ProviderService, pk=ps_id, provider=provider)
            ps.delete()
            messages.success(request, f'Service "{ps.name}" deleted successfully.')
            return redirect('manage_provider_services')
            
        form = ProviderServiceForm(request.POST, request.FILES)
        if form.is_valid():
            ps = form.save(commit=False)
            ps.provider = provider
            service, _ = Service.objects.get_or_create(
                name=form.cleaned_data['name'],
                sub_category=form.cleaned_data['sub_category']
            )
            ps.service = service
            ps.save()
            form.save_m2m()
            messages.success(request, 'Service added successfully!')
            return redirect('manage_provider_services')
    else:
        form = ProviderServiceForm()
    
    return render(request, 'providers/manage_services.html', {'form': form, 'provider_services': provider_services})


@login_required
@user_passes_test(is_service_provider, login_url='/accounts/login/')
def manage_working_hours(request):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    working_hours = WorkingHours.objects.filter(provider=provider)
    
    if request.method == 'POST':
        form = WorkingHoursForm(request.POST)
        if form.is_valid():
            wh = form.save(commit=False)
            wh.provider = provider
            wh.save()
            messages.success(request, 'Working hours added successfully!')
            return redirect('manage_working_hours')
    else:
        form = WorkingHoursForm()
    
    return render(request, 'providers/manage_working_hours.html', {'form': form, 'working_hours': working_hours})


@login_required
@user_passes_test(is_service_provider, login_url='/accounts/login/')
def manage_blocked_slots(request):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    blocked_slots = BlockedSlot.objects.filter(provider=provider)
    
    if request.method == 'POST':
        form = ProviderBlockedSlotForm(request.POST)
        if form.is_valid():
            bs = form.save(commit=False)
            bs.provider = provider
            
            # Check for conflicts with existing appointments before saving
            from appointments.models import Appointment
            from django.db.models import Q
            
            conflicts = Appointment.objects.filter(
                Q(date=bs.date),
                Q(status__in=['pending', 'approved', 'paid']),
                Q(provider_service__provider=provider),
                Q(time_slot__start_time__lt=bs.end_time) & Q(time_slot__end_time__gt=bs.start_time)
            )
            
            if conflicts.exists():
                messages.error(request, 'This blocked slot conflicts with an existing appointment.')
            else:
                try:
                    bs.save()
                    messages.success(request, 'Blocked slot added successfully!')
                except IntegrityError:
                    messages.error(request, 'A blocked slot with these details already exists.')
            return redirect('manage_blocked_slots')
    else:
        form = ProviderBlockedSlotForm()
    return render(request, 'providers/manage_blocked_slots.html', {'form': form, 'blocked_slots': blocked_slots})




@login_required
def add_time_slot(request):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    
    if request.method == 'POST':
        form = ProviderTimeSlotForm(request.POST)
        if form.is_valid():
            ts = form.save(commit=False)
            ts.provider = provider

            # Check conflicts with appointments
            conflicts = Appointment.objects.filter(
                date=ts.date,
                status__in=['pending', 'approved', 'paid'],
                provider_service__provider=provider,
                time_slot__start_time__lt=ts.end_time,
                time_slot__end_time__gt=ts.start_time
            )

            # Check conflicts with blocked slots
            conflicting_blocked_slots = BlockedSlot.objects.filter(
                provider=provider,
                date=ts.date,
                start_time__lt=ts.end_time,
                end_time__gt=ts.start_time
            )

            if conflicts.exists() or conflicting_blocked_slots.exists():
                messages.error(request, 'This time slot conflicts with existing appointments or blocked slots.')
                return redirect('add_time_slot')

            # Validate past date
            if ts.date < date.today():
                messages.error(request, 'You cannot add a time slot for a past date.')
                return redirect('add_time_slot')

            # Validate working hours
            day_of_week = ts.date.weekday()
            try:
                working_hours = WorkingHours.objects.get(provider=provider, day_of_week=day_of_week)
                if ts.start_time < working_hours.start_time or ts.end_time > working_hours.end_time:
                    messages.error(request, 'Time slot is outside of your defined working hours for that day.')
                    return redirect('add_time_slot')
            except WorkingHours.DoesNotExist:
                messages.error(request, 'You have not set working hours for that day of the week.')
                return redirect('add_time_slot')

            # Save slot if all validations pass
            ts.save()
            messages.success(request, 'Time slot added successfully!')
            return redirect('add_time_slot')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = ProviderTimeSlotForm()

    time_slots = ProviderTimeSlot.objects.filter(provider=provider).order_by('date', 'start_time')
    
    return render(request, 'providers/add_time_slot.html', {'form': form, 'time_slots': time_slots})



@login_required
@user_passes_test(is_service_provider, login_url='/accounts/login/')
def edit_time_slot(request, pk):
    provider = request.user.service_provider_profile
    ts = get_object_or_404(ProviderTimeSlot, pk=pk, provider=provider)

    if request.method == 'POST':
        form = ProviderTimeSlotForm(request.POST, instance=ts)
        if form.is_valid():
            updated_ts = form.save(commit=False)

            # Check conflicts with appointments
            conflicts = Appointment.objects.filter(
                date=updated_ts.date,
                status__in=['pending', 'approved', 'paid'],
                provider_service__provider=provider,
                time_slot__start_time__lt=updated_ts.end_time,
                time_slot__end_time__gt=updated_ts.start_time
            ).exclude(pk=ts.pk)  # exclude current slot

            # Check conflicts with blocked slots
            conflicting_blocked_slots = BlockedSlot.objects.filter(
                provider=provider,
                date=updated_ts.date,
                start_time__lt=updated_ts.end_time,
                end_time__gt=updated_ts.start_time
            ).exclude(pk=ts.pk)  # exclude current slot if needed

            if conflicts.exists() or conflicting_blocked_slots.exists():
                messages.error(request, 'This time slot conflicts with existing appointments or blocked slots.')
                return redirect('edit_time_slot', pk=pk)

            # Validate past date
            if updated_ts.date < date.today():
                messages.error(request, 'You cannot set a time slot for a past date.')
                return redirect('edit_time_slot', pk=pk)

            # Validate working hours
            day_of_week = updated_ts.date.weekday()
            try:
                working_hours = WorkingHours.objects.get(provider=provider, day_of_week=day_of_week)
                if updated_ts.start_time < working_hours.start_time or updated_ts.end_time > working_hours.end_time:
                    messages.error(request, 'Time slot is outside of your defined working hours for that day.')
                    return redirect('edit_time_slot', pk=pk)
            except WorkingHours.DoesNotExist:
                messages.error(request, 'You have not set working hours for that day of the week.')
                return redirect('edit_time_slot', pk=pk)

            # Save if everything passes
            updated_ts.save()
            messages.success(request, 'Time slot updated successfully!')
            return redirect('add_time_slot')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = ProviderTimeSlotForm(instance=ts)

    return render(request, 'providers/edit_time_slot.html', {'form': form, 'ts': ts})

@login_required
@user_passes_test(is_service_provider, login_url='/accounts/login/')
def delete_time_slot(request, pk):
    ts = get_object_or_404(ProviderTimeSlot, pk=pk, provider=request.user.service_provider_profile)
    if request.method == 'POST':
        if ts.is_booked:
            messages.error(request, 'Cannot delete a time slot that is already booked.')
        else:
            ts.delete()
            messages.success(request, 'Time slot deleted successfully!')
    return redirect('add_time_slot')


@login_required
@user_passes_test(is_service_provider, login_url='/accounts/login/')
def manage_appointments(request):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    pending_appointments = Appointment.objects.filter(provider_service__provider=provider, status='pending')
    approved_appointments = Appointment.objects.filter(provider_service__provider=provider, status='approved')
    
    if request.method == 'POST':
        appt_id = request.POST.get('appointment_id')
        action = request.POST.get('action')
        appt = get_object_or_404(Appointment, id=appt_id, provider_service__provider=provider)
        
        if action == 'approve':
            appt.status = 'approved'
            appt.save()
            
            # NEW: Mark the time slot as booked
            appt.time_slot.is_booked = True
            appt.time_slot.save()
            
            messages.success(request, 'Appointment approved!')
        elif action == 'reject':
            appt.status = 'rejected'
            appt.save()
            messages.info(request, 'Appointment rejected.')
            
        return redirect('manage_appointments')
    
    context = {
        'provider': provider,
        'pending_appointments': pending_appointments,
        'approved_appointments': approved_appointments,
    }
    return render(request, 'providers/manage_appointments.html', context)


@login_required
@user_passes_test(is_service_provider, login_url='/accounts/login/')
def edit_provider_service(request, pk):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    ps = get_object_or_404(ProviderService, pk=pk, provider=provider)
    
    if request.method == 'POST':
        form = ProviderServiceForm(request.POST, request.FILES, instance=ps)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully!')
            return redirect('manage_provider_services')
    else:
        form = ProviderServiceForm(instance=ps)
    
    return render(request, 'providers/edit_provider_service.html', {'form': form, 'ps': ps})


@login_required
@user_passes_test(is_service_provider, login_url='/accounts/login/')
def delete_blocked_slot(request, pk):
    blocked_slot = get_object_or_404(BlockedSlot, pk=pk)
    if request.method == 'POST':
        blocked_slot.delete()
        messages.success(request, 'Blocked slot deleted successfully!')
    return redirect('manage_blocked_slots')

@login_required
@user_passes_test(is_service_provider, login_url='/accounts/login/')
def remove_offered_service(request, pk):
    ps = get_object_or_404(ProviderService, pk=pk, provider=request.user.service_provider_profile)
    if request.method == 'POST':
        ps.delete()
        messages.success(request, f'Service "{ps.name}" deleted successfully!')
    return redirect('manage_provider_services')

# In your views.py

@login_required
def get_subcategories(request, category_id):  # Accept category_id as an argument
    if category_id:
        subcategories = ServiceSubCategory.objects.filter(category_id=category_id).values('id', 'name')
        return JsonResponse(list(subcategories), safe=False)
    return JsonResponse([], safe=False)


def get_available_time_slots(request):
    provider_service_id = request.GET.get('provider_service_id')
    date_str = request.GET.get('date')
    
    try:
        ps = get_object_or_404(ProviderService, id=provider_service_id)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, ProviderService.DoesNotExist):
        return JsonResponse([], safe=False)
    
    time_slots = ProviderTimeSlot.objects.filter(
        provider=ps.provider,
        date=date,
        is_booked=False
    ).values('id', 'start_time', 'end_time')
    
    data = [{'id': ts['id'], 'start_time': ts['start_time'].strftime('%H:%M')} for ts in time_slots]
    return JsonResponse(data, safe=False)

def create_checkout_session(request, appt_id):
    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, pk=appt_id)
        
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': int(appointment.provider_service.price * 100),
                            'product_data': {
                                'name': f"{appointment.provider_service.name} on {appointment.date} at {appointment.time_slot.start_time}",
                            },
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=f"{settings.DOMAIN_NAME}/payment-success/?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.DOMAIN_NAME}/payment-cancel/",
                metadata={
                    'appointment_id': appointment.pk,
                }
            )
            return JsonResponse({'sessionId': checkout_session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return HttpResponse(status=405)

@login_required
def payment_success(request):
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            messages.success(request, 'Payment successful! Your appointment is confirmed.')
            return redirect('appointment_list')
        except stripe.error.StripeError as e:
            messages.error(request, f'Payment verification failed: {e}. Please check your appointments list.')
            return redirect('appointment_list')
    messages.error(request, 'Payment success page accessed without a valid session ID.')
    return redirect('appointment_list')

@login_required
def payment_cancel(request):
    messages.info(request, 'Payment was cancelled. Your appointment is still pending payment.')
    return redirect('appointment_list')

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        appointment_id = session.get('metadata', {}).get('appointment_id')

        if appointment_id:
            try:
                appointment = Appointment.objects.get(pk=appointment_id)
                if session.get('payment_status') == 'paid':
                    appointment.status = 'paid'
                    appointment.save()
                else:
                    appointment.status = 'failed'
                    appointment.save()
            except Appointment.DoesNotExist:
                pass
    elif event['type'] == 'checkout.session.async_payment_succeeded':
        session = event['data']['object']
        pass
    elif event['type'] == 'checkout.session.async_payment_failed':
        session = event['data']['object']
        pass

    return HttpResponse(status=200)

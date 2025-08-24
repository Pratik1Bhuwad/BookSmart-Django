# appointments/admin.py
from django.contrib import admin

# Corrected imports for distributed models
from .models import Appointment
from accounts.models import UserRole
from providers.models import ProviderService, ServiceProvider, WorkingHours, BlockedSlot, ServiceLocation,ProviderTimeSlot
from services.models import Service, ServiceCategory, ServiceSubCategory


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role',)
    list_filter = ('role',)
    search_fields = ('user__username', 'role',)
    raw_id_fields = ('user',)

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    list_filter = ('name',)

@admin.register(ServiceSubCategory)
class ServiceSubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'category__name',)
    list_filter = ('category',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'sub_category',)
    search_fields = ('name',)
    list_filter = ('sub_category__category',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    # Updated to reflect new Appointment model fields
    list_display = ('client', 'provider_service', 'date', 'status', 'booked_on')
    list_filter = ('status', 'provider_service__sub_category__category', 'provider_service__provider__user')
    search_fields = ('client__username', 'provider_service__name')
    date_hierarchy = 'date'
    raw_id_fields = ('client', 'provider_service')

@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'phone_number', 'bio')
    search_fields = ('user__username', 'location')
    raw_id_fields = ('user',)

@admin.register(ProviderService)
class ProviderServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'sub_category', 'price', 'duration_minutes')
    search_fields = ('name', 'provider__user__username')
    list_filter = ('sub_category__category', 'provider')
    raw_id_fields = ('provider', 'sub_category')
    filter_horizontal = ('locations',)

@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ('provider', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('provider', 'day_of_week')
    raw_id_fields = ('provider',)

@admin.register(BlockedSlot)
class BlockedSlotAdmin(admin.ModelAdmin):
    list_display = ('provider', 'date', 'start_time', 'end_time')
    list_filter = ('provider', 'date')
    search_fields = ('provider__user__username', 'reason')
    raw_id_fields = ('provider',)

@admin.register(ProviderTimeSlot)
class ProviderTimeSlotAdmin(admin.ModelAdmin):
    list_display = ('provider', 'date', 'start_time', 'end_time', 'is_booked')
    list_filter = ('provider', 'date', 'is_booked')
    search_fields = ('provider__user__username',)
    date_hierarchy = 'date'
    raw_id_fields = ('provider',)

@admin.register(ServiceLocation)
class ServiceLocationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

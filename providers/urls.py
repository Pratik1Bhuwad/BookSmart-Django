# providers/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('manage-services/', views.manage_provider_services, name='manage_provider_services'),
    path('manage-working-hours/', views.manage_working_hours, name='manage_working_hours'),
    path('manage-blocked-slots/', views.manage_blocked_slots, name='manage_blocked_slots'),
    path('add-time-slot/', views.add_time_slot, name='add_time_slot'),
    path('edit-time-slot/<int:pk>/', views.edit_time_slot, name='edit_time_slot'), # NEW URL
    path('delete-time-slot/<int:pk>/', views.delete_time_slot, name='delete_time_slot'), # NEW URL
    path('manage-appointments/', views.manage_appointments, name='manage_appointments'),
    path('manage-blocked-slots/delete/<int:pk>/', views.delete_blocked_slot, name='delete_blocked_slot'),
    # This URL now accepts an integer argument named 'category_id'
    path('api/subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),
    path('api/time-slots/', views.get_available_time_slots, name='get_available_time_slots'),
    path('remove-offered-service/<int:pk>/', views.remove_offered_service, name='remove_offered_service'),
    path('edit-provider-service/<int:pk>/', views.edit_provider_service, name='edit_provider_service'),
]
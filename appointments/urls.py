# appointments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('my-appointments/', views.client_appointments, name='appointment_list'), # Corrected URL name
    path('category/<int:category_id>/', views.select_subcategory, name='select_subcategory'),
    path('subcategory/<int:subcategory_id>/', views.select_provider_service, name='select_provider_service'),
    path('request-appointment/<int:provider_service_id>/', views.appointment_request, name='appointment_request'),
    path('my-appointments/', views.client_appointments, name='client_appointments'),
]
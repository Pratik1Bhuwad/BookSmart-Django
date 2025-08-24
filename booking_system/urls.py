# booking_system/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from appointments import views as appointment_views
from accounts import views as accounts_views
from providers import views as providers_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/login/redirect/', accounts_views.login_redirect, name='login_redirect'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('appointments/', include('appointments.urls')),
    path('providers/', include('providers.urls')),
    path('services/', include('services.urls')),
    path('', appointment_views.home_page, name='home'),
    path('logout_message/', TemplateView.as_view(template_name='accounts/logout_message.html'), name='logout_message'),
    
    path('create-checkout-session/<int:appt_id>/', providers_views.create_checkout_session, name='create_checkout_session'),
    path('payment-success/', providers_views.payment_success, name='payment_success'),
    path('payment-cancel/', providers_views.payment_cancel, name='payment_cancel'),
    path('stripe-webhook/', providers_views.stripe_webhook, name='stripe_webhook'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
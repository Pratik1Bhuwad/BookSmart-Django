# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.urls import reverse
from .models import UserRole # NEW: Corrected import

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! You are now logged in.')
            
            if hasattr(user, 'userrole') and user.userrole.role == 'service_provider':
                return redirect(reverse('provider_dashboard'))
            else:
                return redirect(reverse('home'))
        else:
            pass
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_redirect(request):
    if hasattr(request.user, 'userrole') and request.user.userrole.role == 'service_provider':
        return redirect(reverse('provider_dashboard'))
    else:
        return redirect(reverse('home'))

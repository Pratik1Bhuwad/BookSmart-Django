# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import UserRole # Corrected import
from providers.models import ServiceProvider

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=UserRole.USER_ROLES,
        initial='client',
        label='Register as'
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            role = self.cleaned_data['role']
            UserRole.objects.create(user=user, role=role)
            if role == 'service_provider':
                ServiceProvider.objects.create(user=user)
        return user

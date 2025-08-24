# accounts/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    USER_ROLES = (
        ('client', 'Client'),
        ('service_provider', 'Service Provider'),
    )
    role = models.CharField(max_length=20, choices=USER_ROLES, default='client')

    def __str__(self):
        return self.user.username + " - " + self.get_role_display()

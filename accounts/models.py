from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        STAFF = 'staff', 'Staff'
        USER = 'user', 'User'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_privileged(self):
        """Admins and staff can see every user's habits and logs."""
        return self.role in (self.Role.ADMIN, self.Role.STAFF)

    def __str__(self):
        return f"{self.username} ({self.role})"

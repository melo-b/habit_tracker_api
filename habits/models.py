from django.conf import settings
from django.db import models

from .validators import validate_not_future


class Habit(models.Model):
    FREQUENCY_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    )

    # The user who owns this habit
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='daily')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def owner(self):
        return self.user

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class HabitLog(models.Model):
    # The specific habit this log belongs to
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField(validators=[validate_not_future])
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            # A habit can only be logged once per day
            models.UniqueConstraint(fields=['habit', 'date'], name='unique_habit_log_per_day'),
        ]

    @property
    def owner(self):
        return self.habit.user

    def __str__(self):
        return f"{self.habit.name} - {self.date} - {'Done' if self.completed else 'Pending'}"

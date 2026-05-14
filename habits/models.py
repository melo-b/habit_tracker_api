from django.db import models
from django.conf import settings

# Create your models here.

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

    def __str__(self):
        return f"{self.name} - {self.user.username}"

class HabitLog(models.Model):
    # The specific habit this log belongs to
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField()
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        # Prevent a user from logging the same habit multiple times on the same day
        unique_together = ['habit', 'date']

    def __str__(self):
        return f"{self.habit.name} - {self.date} - {'Done' if self.completed else 'Pending'}"
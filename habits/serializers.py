import datetime
from rest_framework import serializers
from .models import Habit, HabitLog

class HabitLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitLog
        fields = ['id', 'habit', 'date', 'completed', 'notes']

    def validate_date(self, value):
        if value > datetime.date.today():
               raise serializers.ValidationError("You cannot log a habit for a future date.")
        return value

class HabitSerializer(serializers.ModelSerializer):
    # This allows us to nest the logs inside the habit payload (read-only)
    logs = HabitLogSerializer(many=True, read_only=True)

    class Meta:
        model = Habit
        fields = ['id', 'user', 'name', 'description', 'frequency', 'created_at', 'logs']
        # We make user read-only so people can't create habits for other users
        read_only_fields = ['user', 'created_at']
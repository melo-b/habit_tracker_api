from rest_framework import serializers
from .models import Habit, HabitLog


class HabitLogSerializer(serializers.ModelSerializer):
    # The future-date rule lives on the model field, so it applies here and in the admin
    class Meta:
        model = HabitLog
        fields = ['id', 'habit', 'date', 'completed', 'notes']

    def validate_habit(self, habit):
        # Only admins may log against habits they don't own
        user = self.context['request'].user
        if not user.is_admin and habit.owner != user:
            raise serializers.ValidationError("Invalid habit.")
        return habit


class HabitSerializer(serializers.ModelSerializer):
    # This allows us to nest the logs inside the habit payload (read-only)
    logs = HabitLogSerializer(many=True, read_only=True)

    class Meta:
        model = Habit
        fields = ['id', 'user', 'name', 'description', 'frequency', 'created_at', 'logs']
        # We make user read-only so people can't create habits for other users
        read_only_fields = ['user', 'created_at']

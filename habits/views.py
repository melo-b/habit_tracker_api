from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .models import Habit, HabitLog
from .serializers import HabitSerializer, HabitLogSerializer
from .permissions import IsOwnerAdminOrStaffReadOnly

class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwnerAdminOrStaffReadOnly]
    
    # Attach built-in DRF Filters
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']

    def get_queryset(self):
        # List-level visibility: Admins/Staff see all, Users see only theirs
        user = self.request.user
        if user.role in ['admin', 'staff']:
            return Habit.objects.all()
        return Habit.objects.filter(user=user)

    def perform_create(self, serializer):
        # Auto-assign the logged-in user to the habit upon creation
        serializer.save(user=self.request.user)

class HabitLogViewSet(viewsets.ModelViewSet):
    serializer_class = HabitLogSerializer
    permission_classes = [IsAuthenticated, IsOwnerAdminOrStaffReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'staff']:
            return HabitLog.objects.all()
        return HabitLog.objects.filter(habit__user=user)
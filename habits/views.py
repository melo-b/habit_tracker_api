from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .models import Habit, HabitLog
from .serializers import HabitSerializer, HabitLogSerializer
from .permissions import IsOwnerAdminOrStaffReadOnly


class OwnerScopedQuerySetMixin:
    """List-level visibility: admins/staff see everything, users only what they own."""
    owner_lookup = 'user'  # ORM path from the model to its owning user

    def get_queryset(self):
        queryset = super().get_queryset()
        if getattr(self, 'swagger_fake_view', False):  # schema generation has no real user
            return queryset.none()
        user = self.request.user
        if user.is_privileged:
            return queryset
        return queryset.filter(**{self.owner_lookup: user})


class HabitViewSet(OwnerScopedQuerySetMixin, viewsets.ModelViewSet):
    queryset = Habit.objects.prefetch_related('logs')
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwnerAdminOrStaffReadOnly]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at', 'id']  # stable default so pagination is deterministic

    def perform_create(self, serializer):
        # Auto-assign the logged-in user to the habit upon creation
        serializer.save(user=self.request.user)


class HabitLogViewSet(OwnerScopedQuerySetMixin, viewsets.ModelViewSet):
    queryset = HabitLog.objects.select_related('habit__user')
    serializer_class = HabitLogSerializer
    permission_classes = [IsAuthenticated, IsOwnerAdminOrStaffReadOnly]
    owner_lookup = 'habit__user'

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date']
    ordering = ['-date', 'id']

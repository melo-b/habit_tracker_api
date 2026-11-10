from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Habit, HabitLog
from .permissions import IsOwnerAdminOrStaffReadOnly
from .serializers import (
    HabitLogSerializer,
    HabitSerializer,
    HabitStatsQuerySerializer,
    HabitStatsSerializer,
    LogTodaySerializer,
)
from .services import compute_stats


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

    @extend_schema(
        parameters=[HabitStatsQuerySerializer],
        responses=HabitStatsSerializer,
        summary="Streaks and completion rate for a habit",
    )
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        habit = self.get_object()
        query = HabitStatsQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        window_days = query.validated_data['days']

        # Uses the prefetched logs, so this adds no extra queries
        completed_dates = [log.date for log in habit.logs.all() if log.completed]
        result = compute_stats(
            completed_dates=completed_dates,
            frequency=habit.frequency,
            today=timezone.localdate(),
            created_on=timezone.localdate(habit.created_at),
            window_days=window_days,
        )
        result.update(frequency=habit.frequency, window_days=window_days)
        return Response(HabitStatsSerializer(result).data)

    @extend_schema(
        request=LogTodaySerializer,
        responses={200: HabitLogSerializer, 201: HabitLogSerializer},
        summary="Mark today's log for a habit (creates or updates; safe to repeat)",
    )
    @action(detail=True, methods=['post'], url_path='log-today')
    def log_today(self, request, pk=None):
        habit = self.get_object()
        body = LogTodaySerializer(data=request.data)
        body.is_valid(raise_exception=True)
        data = body.validated_data

        log, created = HabitLog.objects.get_or_create(
            habit=habit,
            date=timezone.localdate(),
            defaults={'completed': data['completed'], 'notes': data.get('notes', '')},
        )
        if not created:
            log.completed = data['completed']
            if 'notes' in data:
                log.notes = data['notes']
            log.save()

        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(HabitLogSerializer(log, context=self.get_serializer_context()).data,
                        status=response_status)


class HabitLogViewSet(OwnerScopedQuerySetMixin, viewsets.ModelViewSet):
    queryset = HabitLog.objects.select_related('habit__user')
    serializer_class = HabitLogSerializer
    permission_classes = [IsAuthenticated, IsOwnerAdminOrStaffReadOnly]
    owner_lookup = 'habit__user'

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date']
    ordering = ['-date', 'id']

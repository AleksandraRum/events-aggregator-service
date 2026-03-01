from django.db import models
from django.db.models import Q
import uuid


class Place(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=256)
    city = models.CharField(max_length=256)
    address = models.CharField(max_length=256)
    seats_pattern = models.CharField(max_length=256)
    changed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)


class Event(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=256)
    place = models.ForeignKey(Place, on_delete=models.PROTECT, related_name='events')
    event_time = models.DateTimeField()
    registration_deadline = models.DateTimeField()
    status = models.CharField(max_length=256)
    number_of_visitors = models.PositiveIntegerField()
    changed_at = models.DateTimeField()
    created_at = models.DateTimeField()
    status_changed_at = models.DateTimeField(null=True, blank=True)


class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    ticket_id = models.UUIDField(db_index=True)
    seat = models.CharField(max_length=32)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    canceled_at = models.DateTimeField(null=True, blank=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['event', 'ticket_id'], condition=Q(canceled_at__isnull=True), name='unique_event_ticket'),
            models.UniqueConstraint(fields=['event', 'seat'], condition=Q(canceled_at__isnull=True), name='unique_event_seat'),
        ]


class SyncState(models.Model):

    class StatusChoices(models.TextChoices):
        FAILED = "failed", "Failed"
        SUCCESS = "success", "Success"
        RUNNING = "running", "Running"

    
    last_changed_at = models.DateTimeField(null=True, blank=True)
    last_sync_time = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(choices=StatusChoices.choices, max_length=20, default=StatusChoices.SUCCESS)
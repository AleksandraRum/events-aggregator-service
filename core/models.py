from django.db import models
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



class SyncState(models.Model):

    class StatusChoices(models.TextChoices):
        FAILED = "failed", "Failed"
        SUCCESS = "success", "Success"
        RUNNING = "running", "Running"

    
    last_changed_at = models.DateTimeField(null=True, blank=True)
    last_sync_time = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(choices=StatusChoices.choices, max_length=20, default=StatusChoices.SUCCESS)
import os
import requests
from core.clients.events_provider import EventsProviderClient
from core.models import Event, Ticket
from rest_framework.exceptions import NotFound, ValidationError
from django.utils import timezone
from core.services.seats import get_seats
from django.db.utils import IntegrityError


def register_ticket(event_id, first_name, last_name, email, seat):
    "Валидация данных для регистрации и сохраненеи записи в БД"
    try:
        event = Event.objects.select_related("place").get(id=event_id)
    except Event.DoesNotExist:
        raise NotFound("Event not found")

    if event.status != 'published':
        raise ValidationError("Event is not published")
    
    now = timezone.now()
    if now >= event.registration_deadline:
         raise ValidationError("Registration is closed")
    ticket = Ticket.objects.filter(event=event, seat=seat, canceled_at__isnull=True).first()
    if ticket:
        if ticket.email == email:
            return ticket.ticket_id
        else:
            raise ValidationError("Seat is not available")
    
    client = EventsProviderClient(
        base_url=os.environ["EVENTS_PROVIDER_BASE_URL"],
        api_key=os.environ["EVENTS_PROVIDER_API_KEY"],
       )
    seats_data = get_seats(event_id)
    available_seats = seats_data["available_seats"]
    if seat not in available_seats:
        raise ValidationError("Seat is not available")
    
    try:
        ticket_id = client.register(event_id, first_name, last_name, email, seat)
    except requests.exceptions.HTTPError as e:
        response = getattr(e, "response", None)
        status_code = getattr(response, "status_code", None)
        if status_code == 404:
            raise NotFound("Event not found")
        if status_code in(400, 401):
            raise ValidationError("Registration failed")
        raise ValidationError("Registration failed")
    try:
        Ticket.objects.create(event=event, ticket_id=ticket_id, seat=seat, email=email)
    except IntegrityError:
        ticket = Ticket.objects.filter(event=event, seat=seat, canceled_at__isnull=True).first()
        if ticket and ticket.email == email: 
            return ticket.ticket_id
        else:
            raise ValidationError("Seat is not available")

    return ticket_id


def unregister_ticket(ticket_id):
    try:
        ticket = Ticket.objects.get(ticket_id=ticket_id)
    except Ticket.DoesNotExist:
        raise NotFound("Ticket not found")
    if ticket.canceled_at is not None:
        raise ValidationError("Ticket was canceled")
    event = ticket.event
    if event.event_time <= timezone.now():
        raise ValidationError("Event is in the past")
    client = EventsProviderClient(
        base_url=os.environ["EVENTS_PROVIDER_BASE_URL"],
        api_key=os.environ["EVENTS_PROVIDER_API_KEY"],
       )
    
    client.unregister(event.id, ticket.ticket_id)
    ticket.canceled_at = timezone.now()
    ticket.save(update_fields=["canceled_at"])

    return {"success": True}
import os
import requests
from core.clients.events_provider import EventsProviderClient
from core.models import Event, Ticket, NotificationOutbox
from rest_framework.exceptions import NotFound, ValidationError
from django.utils import timezone
from core.services.seats import get_seats
from django.db.utils import IntegrityError
from django.db import transaction


def register_ticket(event_id, first_name, last_name, email, seat):
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
    payload = {
        "message": f"Вы успешно зарегистрированы на мероприятие - {event.name}",
        "reference_id": str(ticket_id),
    }
    with transaction.atomic():
        try:
            Ticket.objects.create(event=event, ticket_id=ticket_id, seat=seat, email=email)
        except IntegrityError:
            ticket = Ticket.objects.filter(event=event, seat=seat, canceled_at__isnull=True).first()
            if ticket and ticket.email == email: 
                return ticket.ticket_id
            else:
                raise ValidationError("Seat is not available")
        NotificationOutbox.objects.create(event_type='ticket_purchased', payload=payload)

    return ticket_id


def unregister_ticket(ticket_id):
    
    ticket = Ticket.objects.filter(ticket_id=ticket_id, canceled_at__isnull=True).order_by("-created_at").first()
    
    if ticket is None:
        if Ticket.objects.filter(ticket_id=ticket_id).exists():
            raise ValidationError("Ticket was canceled")
        else:
            raise NotFound("Ticket not found")
    event = ticket.event
    client = EventsProviderClient(
        base_url=os.environ["EVENTS_PROVIDER_BASE_URL"],
        api_key=os.environ["EVENTS_PROVIDER_API_KEY"],
       )
    try:
        client.unregister(event.id, ticket.ticket_id)
    except requests.exceptions.HTTPError as e:
        response = getattr(e, "response", None)
        status_code = getattr(response, "status_code", None)
        if status_code == 404:
            raise NotFound("Ticket not found")
        if status_code in(400, 401):
            raise ValidationError("Unregistration failed")
        raise ValidationError("Unregistration failed")
    ticket.canceled_at = timezone.now()
    ticket.save(update_fields=["canceled_at"])

    return {"success": True}
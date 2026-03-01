from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from core.serializers import EventListSerializer, EventDetailSerializer, RegisterSerializer
from core.models import Event
from core.pagination import ListEventPagination
from rest_framework import status
from core.celery_task import sync_events_task
from core.services.seats import get_seats
from core.services.tickets import register_ticket, unregister_ticket

class HealthView(APIView):
    def get(self, request):
        return Response({'status': 'ok'})


class EventGetListView(ListAPIView):
    serializer_class = EventListSerializer
    pagination_class = ListEventPagination

    def get_queryset(self):
        queryset = Event.objects.select_related('place')
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(event_time__date__gte=date_from)
        queryset = queryset.order_by('-event_time')
        return queryset


class EventDetailView(RetrieveAPIView):
    serializer_class = EventDetailSerializer
    queryset = Event.objects.select_related('place')
    lookup_url_kwarg = 'event_id'


class SyncTriggerView(APIView):
    def post(self, request):
        sync_events_task.delay()
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)
    

class SeatsGetView(APIView):
    def get(self, request, event_id):
        seats = get_seats(event_id)
        return Response(seats, status=status.HTTP_200_OK)
    

class RegisterPostView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        ticket_id = register_ticket(
            event_id=data["event_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            seat=data["seat"]
        )
        return Response(
            {"ticket_id": ticket_id},
            status=status.HTTP_201_CREATED
        )
    
class RegisterDeleteView(APIView):
    def delete(self, request, ticket_id):
        res = unregister_ticket(ticket_id)
        return Response(res, status=status.HTTP_200_OK)

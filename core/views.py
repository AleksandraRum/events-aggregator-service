from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from core.serializers import EventListSerializer, EventDetailSerializer
from core.models import Event
from core.pagination import ListEventPagination
from rest_framework import status
from core.celery_task import sync_events_task

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

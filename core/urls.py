from django.urls import path
from core.views import HealthView, EventGetListView

urlpatterns = [
    path('health/', HealthView.as_view()),
    path('events/', EventGetListView.as_view()),
]
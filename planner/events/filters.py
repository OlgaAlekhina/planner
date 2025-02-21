from rest_framework import filters
from .models import Event


class EventFilter(filters.FilterSet):
    class Meta:
        model = Event
        fields = ('start_date', 'end_date')
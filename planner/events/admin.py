from django.contrib import admin
from .models import Event, EventMeta, CanceledEvent

admin.site.register(Event)
admin.site.register(EventMeta)
admin.site.register(CanceledEvent)


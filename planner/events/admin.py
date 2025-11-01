from django.contrib import admin
from .models import Event, EventMeta, CanceledEvent, EventUser

admin.site.register(EventMeta)
admin.site.register(CanceledEvent)


class EventUserInline(admin.TabularInline):
    model = EventUser
    extra = 1
    autocomplete_fields = ['groupuser']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'start_date']
    search_fields = ['title', 'author']
    inlines = [EventUserInline]



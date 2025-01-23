from django.contrib import admin
from .models import Event, Registration, Workshop, Guest, UserRegistration, Club

# Register your models here.

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date')
    search_fields = ('title', 'event_date', 'venue')
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date')
    search_fields = ('title', 'event_date', 'venue')

class GuestAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date')
    search_fields = ('title', 'event_date', 'venue')


admin.site.register(Event, EventAdmin)
admin.site.register(Registration)
admin.site.register(Workshop, WorkshopAdmin)
admin.site.register(Guest, GuestAdmin)
admin.site.register(UserRegistration)
admin.site.register(Club)

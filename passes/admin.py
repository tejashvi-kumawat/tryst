from django.contrib import admin
from .models import Pass, Pronite, Slot



class ProniteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class SlotAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'start_time', 'end_time', 'capacity')


class PassAdmin(admin.ModelAdmin):
    list_display = ('id', 'userId', 'slotId', 'entry', 'entryTime')
    search_fields = ('userId', 'slotId')


# Register your models here.
admin.site.register(Pronite, ProniteAdmin)
admin.site.register(Slot)
admin.site.register(Pass)

from django.contrib import admin
from .models import Profile, College, Pac


# Register your models here.

class CollegeAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'college_ID')
    search_fields = ('name', 'city', 'state', 'college_ID')


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'email_ID', 'phone_Number', 'category', 'user_ID')
    search_fields = ('name', 'email_ID', 'phone_Number', 'category', 'user_ID')


class PacAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'category')
    search_fields = ('name', 'email', 'phone', 'category')


admin.site.register(Pac, PacAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(College, CollegeAdmin)

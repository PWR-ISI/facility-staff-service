from django.contrib import admin
from .models import Facility, FacilityStaff

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'is_active', 'created_at')

@admin.register(FacilityStaff)
class FacilityStaffAdmin(admin.ModelAdmin):
    list_display = ('facility', 'role', 'user_id', 'is_active')

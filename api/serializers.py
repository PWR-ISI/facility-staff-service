from rest_framework import serializers
from .models import Facility, FacilityStaff

class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ('id', 'name', 'address', 'city', 'phone', 'email', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')

class FacilityStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilityStaff
        fields = ('id', 'facility', 'user_id', 'role', 'specialization', 'license_number', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')

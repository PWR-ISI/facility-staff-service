from rest_framework import serializers
from .models import Facility, FacilityStaff, Doctor

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

class DoctorSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source='facility.name', read_only=True, default=None)

    class Meta:
        model = Doctor
        fields = ('id', 'user_id', 'email', 'first_name', 'last_name', 'specialization',
                  'license_number', 'facility', 'facility_name', 'photo_url', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')

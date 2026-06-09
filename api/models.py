from django.db import models

class Facility(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'facilities'

    def __str__(self):
        return self.name


class FacilityStaff(models.Model):
    ROLES = (('doctor', 'Doctor'), ('nurse', 'Nurse'), ('receptionist', 'Receptionist'), ('admin', 'Admin'))

    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='staff')
    user_id = models.IntegerField()
    role = models.CharField(max_length=20, choices=ROLES)
    specialization = models.CharField(max_length=100, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'facility_staff'
        unique_together = ('facility', 'user_id')

    def __str__(self):
        return f"{self.role} at {self.facility.name}"


class Doctor(models.Model):
    """Doctor directory entry. `user_id` == auth-identity cognito_sub == schedule doctor_id."""
    user_id = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=100, blank=True)
    facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctors')
    photo_url = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'doctors'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} ({self.specialization})"


class AuditLog(models.Model):
    """Local audit trail for administrative actions in this service."""
    actor_id = models.CharField(max_length=255, blank=True)
    actor_role = models.CharField(max_length=20, blank=True)
    action = models.CharField(max_length=50)
    target_type = models.CharField(max_length=50, blank=True)
    target_id = models.CharField(max_length=255, blank=True)
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'facility_audit_log'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} by {self.actor_id} at {self.timestamp}"

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

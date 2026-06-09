from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacilityViewSet, FacilityStaffViewSet, DoctorViewSet, health_check

router = DefaultRouter()
router.register(r'facilities', FacilityViewSet)
router.register(r'staff', FacilityStaffViewSet)
router.register(r'doctors', DoctorViewSet, basename='doctor')

urlpatterns = [
    path('health/', health_check, name='health'),
    path('', include(router.urls))
]

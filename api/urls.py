from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacilityViewSet, FacilityStaffViewSet, health_check

router = DefaultRouter()
router.register(r'facilities', FacilityViewSet)
router.register(r'staff', FacilityStaffViewSet)

urlpatterns = [
    path('health/', health_check, name='health'),
    path('', include(router.urls))
]

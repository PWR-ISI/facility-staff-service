from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Facility, FacilityStaff
from .serializers import FacilitySerializer, FacilityStaffSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'healthy'}, status=status.HTTP_200_OK)

class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.filter(is_active=True)
    serializer_class = FacilitySerializer
    permission_classes = [IsAuthenticated]

class FacilityStaffViewSet(viewsets.ModelViewSet):
    queryset = FacilityStaff.objects.filter(is_active=True)
    serializer_class = FacilityStaffSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['facility', 'role', 'user_id']

import json
import logging
from pathlib import Path

from jsonschema import Draft202012Validator
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import Facility, FacilityStaff, Doctor, AuditLog
from .serializers import FacilitySerializer, FacilityStaffSerializer, DoctorSerializer
from .s3_utils import upload_staff_photo
from common.auth import IsAuthenticated, IsAdmin, IsAdminOrStaff

logger = logging.getLogger(__name__)

# Load the JSON Schema once at import time (Draft 2020-12).
_SCHEMA_PATH = Path(__file__).resolve().parent / 'schemas' / 'create_doctor.schema.json'
_DOCTOR_VALIDATOR = Draft202012Validator(json.loads(_SCHEMA_PATH.read_text(encoding='utf-8')))


def _schema_errors(payload):
    """Return a list of {field, message} for JSON Schema violations (or [])."""
    errors = sorted(_DOCTOR_VALIDATOR.iter_errors(payload), key=lambda e: list(e.path))
    return [
        {'field': '.'.join(str(p) for p in e.path) or '(root)', 'message': e.message}
        for e in errors
    ]


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'healthy'}, status=status.HTTP_200_OK)


class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.filter(is_active=True)
    serializer_class = FacilitySerializer
    authentication_classes = []

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdmin()]


class FacilityStaffViewSet(viewsets.ModelViewSet):
    queryset = FacilityStaff.objects.filter(is_active=True)
    serializer_class = FacilityStaffSerializer
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    filterset_fields = ['facility', 'role', 'user_id']


class DoctorViewSet(viewsets.ModelViewSet):
    """
    Doctor directory.
      - list/retrieve: any authenticated user (patient search by specialization/facility/q)
      - create/update/delete: admin only
    """
    queryset = Doctor.objects.filter(is_active=True)
    serializer_class = DoctorSerializer
    authentication_classes = []
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        # Admin or front-desk clerk may register doctors (DoctorRegistrationClerk).
        return [IsAdminOrStaff()]

    def get_queryset(self):
        qs = Doctor.objects.filter(is_active=True)
        spec = self.request.query_params.get('specialization')
        facility = self.request.query_params.get('facility')
        q = self.request.query_params.get('q')
        if spec:
            qs = qs.filter(specialization__icontains=spec)
        if facility:
            qs = qs.filter(facility_id=facility)
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(specialization__icontains=q)
            )
        return qs

    @extend_schema(
        summary='Search doctors',
        parameters=[
            OpenApiParameter('specialization', str, description='Filter by specialization (contains)'),
            OpenApiParameter('facility', int, description='Filter by facility id'),
            OpenApiParameter('q', str, description='Free-text search over name/specialization'),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary='Create a doctor profile (admin only)',
        description='Validates the payload with JSON Schema (400 on error), optionally uploads a profile '
                    'photo to S3 (LocalStack), stores the doctor and writes an audit entry. '
                    'Multipart form: text fields + optional `photo` file. `user_id` is the auth cognito_sub.',
        request=None,
        responses={201: DoctorSerializer, 400: OpenApiResponse(description='Validation errors: {errors: [{field, message}]}')},
    )
    def create(self, request, *args, **kwargs):
        payload = {
            k: request.data.get(k)
            for k in ('user_id', 'email', 'first_name', 'last_name', 'specialization', 'license_number', 'facility_id')
            if request.data.get(k) not in (None, '')
        }

        # 1) Rigorous JSON Schema validation -> 400 at the controller.
        errors = _schema_errors(payload)
        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        if Doctor.objects.filter(user_id=payload['user_id']).exists():
            return Response({'errors': [{'field': 'user_id', 'message': 'Doctor already exists for this account'}]},
                            status=status.HTTP_400_BAD_REQUEST)

        facility = Facility.objects.filter(pk=payload['facility_id']).first()
        if not facility:
            return Response({'errors': [{'field': 'facility_id', 'message': 'Facility not found'}]},
                            status=status.HTTP_400_BAD_REQUEST)

        # 2) Optional profile photo -> LocalStack S3.
        photo_url = ''
        photo = request.FILES.get('photo')
        if photo:
            try:
                photo_url = upload_staff_photo(photo, payload['user_id'])
            except Exception as exc:
                logger.error('Doctor photo upload failed: %s', exc)
                return Response({'errors': [{'field': 'photo', 'message': f'Upload failed: {exc}'}]},
                                status=status.HTTP_400_BAD_REQUEST)

        doctor = Doctor.objects.create(
            user_id=payload['user_id'],
            email=payload['email'],
            first_name=payload['first_name'],
            last_name=payload['last_name'],
            specialization=payload['specialization'],
            license_number=payload.get('license_number', ''),
            facility=facility,
            photo_url=photo_url,
        )

        # 3) Audit: admin id + timestamp (timestamp via auto_now_add).
        AuditLog.objects.create(
            actor_id=getattr(request, 'user_id', '') or '',
            actor_role=getattr(request, 'user_role', '') or '',
            action='create_doctor',
            target_type='doctor',
            target_id=str(doctor.id),
            details={
                'doctor_user_id': doctor.user_id,
                'email': doctor.email,
                'specialization': doctor.specialization,
                'facility_id': facility.id,
            },
        )
        logger.info('Admin %s created doctor %s', getattr(request, 'user_id', '?'), doctor.user_id)
        return Response(DoctorSerializer(doctor).data, status=status.HTTP_201_CREATED)

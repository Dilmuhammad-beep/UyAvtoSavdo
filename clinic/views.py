from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from clinic.filters import DiseaseFilter, DoctorFilter, PatientFilter
from clinic.models import Disease, Doctor, Patient, User
from clinic.permissions import IsAdminRole, IsClinicianOrAdmin, IsReceptionOrAbove
from clinic.serializers import (
    DiseaseSerializer,
    DoctorSerializer,
    PatientProfileSerializer,
    PatientSerializer,
)


# ── API ViewSets ──────────────────────────────────────────────

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    filterset_class = DoctorFilter
    search_fields = ['first_name', 'last_name', 'specialty', 'department']
    ordering_fields = ['last_name', 'first_name', 'department', 'created_at']

    def get_permissions(self):
        if self.action in ('create', 'destroy'):
            return [IsAdminRole()]
        if self.action in ('update', 'partial_update'):
            return [IsClinicianOrAdmin()]
        return [IsReceptionOrAbove()]

    @action(detail=True, methods=['get'])
    def patients(self, request, pk=None):
        doctor = self.get_object()
        patients = doctor.patients.all()
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.select_related('doctor').all()
    filterset_class = PatientFilter
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    ordering_fields = ['last_name', 'first_name', 'date_of_birth', 'created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PatientProfileSerializer
        return PatientSerializer

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAdminRole()]
        if self.action == 'create':
            return [IsReceptionOrAbove()]
        return [IsClinicianOrAdmin()]

    @action(detail=True, methods=['get'])
    def diseases(self, request, pk=None):
        patient = self.get_object()
        diseases = patient.diseases.all()
        serializer = DiseaseSerializer(diseases, many=True)
        return Response(serializer.data)


class DiseaseViewSet(viewsets.ModelViewSet):
    queryset = Disease.objects.select_related('patient').all()
    serializer_class = DiseaseSerializer
    filterset_class = DiseaseFilter
    search_fields = ['icd_code', 'name', 'description']
    ordering_fields = ['diagnosed_date', 'severity', 'created_at']

    def get_permissions(self):
        if self.action in ('create', 'destroy'):
            return [IsAdminRole()]
        if self.action in ('update', 'partial_update'):
            return [IsClinicianOrAdmin()]
        return [IsClinicianOrAdmin()]


# ── Template Views ────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    context = {
        'doctor_count': Doctor.objects.count(),
        'patient_count': Patient.objects.count(),
        'disease_count': Disease.objects.count(),
        'recent_patients': Patient.objects.select_related('doctor').order_by('-created_at')[:5],
        'recent_diseases': Disease.objects.select_related('patient').order_by('-created_at')[:5],
    }
    return render(request, 'clinic/dashboard.html', context)


@login_required
def doctor_list_view(request):
    doctors = Doctor.objects.all()
    q = request.GET.get('q', '')
    department = request.GET.get('department', '')
    if q:
        from django.db.models import Q
        doctors = doctors.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(specialty__icontains=q)
        )
    if department:
        doctors = doctors.filter(department=department)
    return render(request, 'clinic/doctor_list.html', {'doctors': doctors, 'q': q, 'department': department})


@login_required
def patient_list_view(request):
    patients = Patient.objects.select_related('doctor').all()
    q = request.GET.get('q', '')
    if q:
        from django.db.models import Q
        patients = patients.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q)
        )
    return render(request, 'clinic/patient_list.html', {'patients': patients, 'q': q})


@login_required
def patient_profile_view(request, pk):
    patient = Patient.objects.select_related('doctor').prefetch_related('diseases').get(pk=pk)
    return render(request, 'clinic/patient_profile.html', {'patient': patient})


@login_required
def disease_list_view(request):
    diseases = Disease.objects.select_related('patient').all()
    q = request.GET.get('q', '')
    severity = request.GET.get('severity', '')
    if q:
        from django.db.models import Q
        diseases = diseases.filter(
            Q(icd_code__icontains=q) | Q(name__icontains=q)
        )
    if severity:
        diseases = diseases.filter(severity=severity)
    return render(request, 'clinic/disease_list.html', {'diseases': diseases, 'q': q, 'severity': severity})

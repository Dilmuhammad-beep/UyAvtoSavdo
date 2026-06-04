from rest_framework import serializers

from clinic.models import Disease, Doctor, Patient, User


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role', 'role_display']
        read_only_fields = ['id']


class DoctorSerializer(serializers.ModelSerializer):
    department_display = serializers.CharField(source='get_department_display', read_only=True)
    patient_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Doctor
        fields = [
            'id', 'first_name', 'last_name', 'specialty', 'department',
            'department_display', 'phone', 'email', 'is_active',
            'patient_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DoctorMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'first_name', 'last_name', 'specialty', 'department']


class DiseaseSerializer(serializers.ModelSerializer):
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)

    class Meta:
        model = Disease
        fields = [
            'id', 'icd_code', 'name', 'description', 'severity',
            'severity_display', 'patient', 'diagnosed_date', 'notes',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PatientSerializer(serializers.ModelSerializer):
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    doctor_detail = DoctorMinimalSerializer(source='doctor', read_only=True)
    diagnosis_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Patient
        fields = [
            'id', 'first_name', 'last_name', 'date_of_birth', 'gender',
            'gender_display', 'phone', 'email', 'address', 'doctor',
            'doctor_detail', 'is_active', 'diagnosis_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PatientProfileSerializer(serializers.ModelSerializer):
    """Full patient profile including doctor and all diagnoses."""
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    doctor_detail = DoctorMinimalSerializer(source='doctor', read_only=True)
    diseases = DiseaseSerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = [
            'id', 'first_name', 'last_name', 'date_of_birth', 'gender',
            'gender_display', 'phone', 'email', 'address', 'doctor',
            'doctor_detail', 'diseases', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

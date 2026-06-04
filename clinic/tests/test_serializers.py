from datetime import date

from django.test import TestCase

from clinic.models import Department, Disease, Doctor, Patient, User
from clinic.serializers import (
    DiseaseSerializer,
    DoctorMinimalSerializer,
    DoctorSerializer,
    PatientProfileSerializer,
    PatientSerializer,
    UserSerializer,
)


class UserSerializerTests(TestCase):
    def test_serialize_user(self):
        user = User.objects.create_user(
            username='admin1', password='p', first_name='Ali',
            last_name='Valiyev', role=User.Role.ADMIN,
        )
        data = UserSerializer(user).data
        self.assertEqual(data['username'], 'admin1')
        self.assertEqual(data['role'], 'admin')
        self.assertEqual(data['role_display'], 'Administrator')
        self.assertNotIn('password', data)

    def test_read_only_id(self):
        user = User.objects.create_user(username='u', password='p')
        data = UserSerializer(user).data
        self.assertIn('id', data)


class DoctorSerializerTests(TestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(
            first_name='Ahmad', last_name='Karimov',
            specialty='Kardiolog', department=Department.CARDIOLOGY,
            phone='+998901234567', email='ahmad@clinic.uz',
        )

    def test_serialize_doctor(self):
        data = DoctorSerializer(self.doctor).data
        self.assertEqual(data['first_name'], 'Ahmad')
        self.assertEqual(data['last_name'], 'Karimov')
        self.assertEqual(data['department'], 'cardiology')
        self.assertEqual(data['department_display'], 'Kardiologiya')
        self.assertEqual(data['patient_count'], 0)

    def test_deserialize_doctor(self):
        payload = {
            'first_name': 'New', 'last_name': 'Doctor',
            'specialty': 'Nevrolog', 'department': 'neurology',
        }
        serializer = DoctorSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        doc = serializer.save()
        self.assertEqual(doc.first_name, 'New')

    def test_minimal_serializer(self):
        data = DoctorMinimalSerializer(self.doctor).data
        self.assertEqual(set(data.keys()), {'id', 'first_name', 'last_name', 'specialty', 'department'})


class PatientSerializerTests(TestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(
            first_name='Doc', last_name='Tor', specialty='General',
        )
        self.patient = Patient.objects.create(
            first_name='Sardor', last_name='Toshmatov',
            date_of_birth=date(1995, 3, 20),
            gender=Patient.Gender.MALE, doctor=self.doctor,
        )

    def test_serialize_patient(self):
        data = PatientSerializer(self.patient).data
        self.assertEqual(data['first_name'], 'Sardor')
        self.assertEqual(data['gender'], 'male')
        self.assertEqual(data['gender_display'], 'Erkak')
        self.assertEqual(data['doctor_detail']['first_name'], 'Doc')
        self.assertEqual(data['diagnosis_count'], 0)

    def test_deserialize_patient(self):
        payload = {
            'first_name': 'New', 'last_name': 'Patient',
            'date_of_birth': '2000-01-01', 'gender': 'female',
            'doctor': self.doctor.pk,
        }
        serializer = PatientSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        patient = serializer.save()
        self.assertEqual(patient.first_name, 'New')

    def test_profile_serializer_includes_diseases(self):
        Disease.objects.create(
            icd_code='J06.9', name='ORVI',
            patient=self.patient, diagnosed_date=date(2024, 1, 10),
        )
        data = PatientProfileSerializer(self.patient).data
        self.assertEqual(len(data['diseases']), 1)
        self.assertEqual(data['diseases'][0]['icd_code'], 'J06.9')


class DiseaseSerializerTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            first_name='Bemor', last_name='Test',
            date_of_birth=date(1990, 6, 15),
            gender=Patient.Gender.FEMALE,
        )
        self.disease = Disease.objects.create(
            icd_code='E11', name='Diabet',
            severity=Disease.Severity.SEVERE,
            patient=self.patient, diagnosed_date=date(2024, 3, 1),
        )

    def test_serialize_disease(self):
        data = DiseaseSerializer(self.disease).data
        self.assertEqual(data['icd_code'], 'E11')
        self.assertEqual(data['severity'], 'severe')
        self.assertIn('severity_display', data)

    def test_deserialize_disease(self):
        payload = {
            'icd_code': 'J00', 'name': 'Shamollash',
            'severity': 'mild', 'patient': self.patient.pk,
            'diagnosed_date': '2024-04-01',
        }
        serializer = DiseaseSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        disease = serializer.save()
        self.assertEqual(disease.name, 'Shamollash')

    def test_invalid_severity(self):
        payload = {
            'icd_code': 'X00', 'name': 'Invalid',
            'severity': 'nonexistent', 'patient': self.patient.pk,
            'diagnosed_date': '2024-01-01',
        }
        serializer = DiseaseSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn('severity', serializer.errors)

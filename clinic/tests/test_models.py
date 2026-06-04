from datetime import date

from django.test import TestCase

from clinic.models import Department, Disease, Doctor, Patient, User


class UserModelTests(TestCase):
    def test_create_user_default_role(self):
        user = User.objects.create_user(username='testuser', password='pass1234')
        self.assertEqual(user.role, User.Role.RECEPTION)

    def test_create_admin_user(self):
        user = User.objects.create_user(
            username='admin1', password='pass1234', role=User.Role.ADMIN,
        )
        self.assertTrue(user.is_admin_role)
        self.assertFalse(user.is_clinician)
        self.assertFalse(user.is_reception)

    def test_create_clinician_user(self):
        user = User.objects.create_user(
            username='clinician1', password='pass1234', role=User.Role.CLINICIAN,
        )
        self.assertTrue(user.is_clinician)
        self.assertFalse(user.is_admin_role)

    def test_create_reception_user(self):
        user = User.objects.create_user(
            username='reception1', password='pass1234', role=User.Role.RECEPTION,
        )
        self.assertTrue(user.is_reception)

    def test_str_with_full_name(self):
        user = User.objects.create_user(
            username='test', password='pass1234',
            first_name='Ali', last_name='Valiyev',
            role=User.Role.ADMIN,
        )
        self.assertIn('Ali Valiyev', str(user))
        self.assertIn('Administrator', str(user))

    def test_str_without_full_name(self):
        user = User.objects.create_user(username='testonly', password='pass1234')
        self.assertIn('testonly', str(user))

    def test_user_ordering(self):
        User.objects.create_user(username='zuser', password='p')
        User.objects.create_user(username='auser', password='p')
        users = list(User.objects.values_list('username', flat=True))
        self.assertEqual(users, sorted(users))


class DoctorModelTests(TestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(
            first_name='Ahmad',
            last_name='Karimov',
            specialty='Kardiolog',
            department=Department.CARDIOLOGY,
            phone='+998901234567',
            email='ahmad@clinic.uz',
        )

    def test_str(self):
        self.assertIn('Ahmad', str(self.doctor))
        self.assertIn('Karimov', str(self.doctor))
        self.assertIn('Kardiologiya', str(self.doctor))

    def test_full_name(self):
        self.assertEqual(self.doctor.full_name, 'Ahmad Karimov')

    def test_patient_count_zero(self):
        self.assertEqual(self.doctor.patient_count, 0)

    def test_patient_count_with_patients(self):
        Patient.objects.create(
            first_name='P1', last_name='L1',
            date_of_birth=date(1990, 1, 1),
            gender=Patient.Gender.MALE,
            doctor=self.doctor,
        )
        Patient.objects.create(
            first_name='P2', last_name='L2',
            date_of_birth=date(1985, 5, 15),
            gender=Patient.Gender.FEMALE,
            doctor=self.doctor,
        )
        self.assertEqual(self.doctor.patient_count, 2)

    def test_default_department(self):
        doc = Doctor.objects.create(
            first_name='Test', last_name='Doc', specialty='General',
        )
        self.assertEqual(doc.department, Department.GENERAL)

    def test_ordering(self):
        Doctor.objects.create(first_name='Z', last_name='ZZZ', specialty='s')
        Doctor.objects.create(first_name='A', last_name='AAA', specialty='s')
        doctors = list(Doctor.objects.values_list('last_name', flat=True))
        self.assertEqual(doctors, sorted(doctors))


class PatientModelTests(TestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(
            first_name='Doc', last_name='Tor', specialty='General',
        )
        self.patient = Patient.objects.create(
            first_name='Sardor',
            last_name='Toshmatov',
            date_of_birth=date(1995, 3, 20),
            gender=Patient.Gender.MALE,
            phone='+998901111111',
            doctor=self.doctor,
        )

    def test_str(self):
        self.assertEqual(str(self.patient), 'Sardor Toshmatov')

    def test_full_name(self):
        self.assertEqual(self.patient.full_name, 'Sardor Toshmatov')

    def test_diagnosis_count_zero(self):
        self.assertEqual(self.patient.diagnosis_count, 0)

    def test_diagnosis_count_with_diseases(self):
        Disease.objects.create(
            icd_code='J06.9', name='ORVI', severity=Disease.Severity.MILD,
            patient=self.patient, diagnosed_date=date(2024, 1, 10),
        )
        Disease.objects.create(
            icd_code='I10', name='Gipertoniya', severity=Disease.Severity.MODERATE,
            patient=self.patient, diagnosed_date=date(2024, 2, 15),
        )
        self.assertEqual(self.patient.diagnosis_count, 2)

    def test_doctor_relationship(self):
        self.assertEqual(self.patient.doctor, self.doctor)
        self.assertIn(self.patient, self.doctor.patients.all())

    def test_doctor_set_null_on_delete(self):
        doctor_id = self.doctor.pk
        self.doctor.delete()
        self.patient.refresh_from_db()
        self.assertIsNone(self.patient.doctor)

    def test_ordering(self):
        Patient.objects.create(
            first_name='Z', last_name='ZZZ',
            date_of_birth=date(2000, 1, 1), gender=Patient.Gender.FEMALE,
        )
        Patient.objects.create(
            first_name='A', last_name='AAA',
            date_of_birth=date(2000, 1, 1), gender=Patient.Gender.MALE,
        )
        patients = list(Patient.objects.values_list('last_name', flat=True))
        self.assertEqual(patients, sorted(patients))


class DiseaseModelTests(TestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(
            first_name='Doc', last_name='Tor', specialty='General',
        )
        self.patient = Patient.objects.create(
            first_name='Bemor', last_name='Test',
            date_of_birth=date(1990, 6, 15),
            gender=Patient.Gender.FEMALE,
            doctor=self.doctor,
        )
        self.disease = Disease.objects.create(
            icd_code='E11',
            name='2-tur diabet',
            description='Qandli diabet 2-tur',
            severity=Disease.Severity.SEVERE,
            patient=self.patient,
            diagnosed_date=date(2024, 3, 1),
            notes='Doimiy nazorat kerak',
        )

    def test_str(self):
        self.assertIn('E11', str(self.disease))
        self.assertIn('2-tur diabet', str(self.disease))

    def test_severity_choices(self):
        self.assertEqual(Disease.Severity.MILD, 'mild')
        self.assertEqual(Disease.Severity.MODERATE, 'moderate')
        self.assertEqual(Disease.Severity.SEVERE, 'severe')
        self.assertEqual(Disease.Severity.CRITICAL, 'critical')

    def test_default_severity(self):
        d = Disease.objects.create(
            icd_code='J00', name='Shamollash',
            patient=self.patient, diagnosed_date=date(2024, 4, 1),
        )
        self.assertEqual(d.severity, Disease.Severity.MODERATE)

    def test_patient_cascade_delete(self):
        patient_id = self.patient.pk
        disease_id = self.disease.pk
        self.patient.delete()
        self.assertFalse(Disease.objects.filter(pk=disease_id).exists())

    def test_ordering_by_diagnosed_date_desc(self):
        Disease.objects.create(
            icd_code='A00', name='Old',
            patient=self.patient, diagnosed_date=date(2020, 1, 1),
        )
        Disease.objects.create(
            icd_code='B00', name='New',
            patient=self.patient, diagnosed_date=date(2025, 1, 1),
        )
        dates = list(Disease.objects.values_list('diagnosed_date', flat=True))
        self.assertEqual(dates, sorted(dates, reverse=True))

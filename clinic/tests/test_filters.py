from datetime import date

from django.test import TestCase

from clinic.filters import DiseaseFilter, DoctorFilter, PatientFilter
from clinic.models import Department, Disease, Doctor, Patient


class DoctorFilterTests(TestCase):
    def setUp(self):
        self.doc1 = Doctor.objects.create(
            first_name='Ahmad', last_name='Karimov',
            specialty='Kardiolog', department=Department.CARDIOLOGY,
        )
        self.doc2 = Doctor.objects.create(
            first_name='Zafar', last_name='Olimov',
            specialty='Nevrolog', department=Department.NEUROLOGY,
        )
        self.doc3 = Doctor.objects.create(
            first_name='Sardor', last_name='Karimov',
            specialty='Dermatolog', department=Department.DERMATOLOGY,
            is_active=False,
        )

    def test_filter_by_department(self):
        f = DoctorFilter({'department': 'cardiology'}, queryset=Doctor.objects.all())
        self.assertEqual(f.qs.count(), 1)
        self.assertEqual(f.qs.first(), self.doc1)

    def test_filter_by_specialty(self):
        f = DoctorFilter({'specialty': 'Kardiolog'}, queryset=Doctor.objects.all())
        self.assertEqual(f.qs.count(), 1)

    def test_filter_by_name(self):
        f = DoctorFilter({'name': 'Karimov'}, queryset=Doctor.objects.all())
        self.assertEqual(f.qs.count(), 2)

    def test_filter_by_is_active(self):
        f = DoctorFilter({'is_active': 'true'}, queryset=Doctor.objects.all())
        self.assertEqual(f.qs.count(), 2)


class PatientFilterTests(TestCase):
    def setUp(self):
        self.doc = Doctor.objects.create(
            first_name='Doc', last_name='Tor', specialty='General',
        )
        self.p1 = Patient.objects.create(
            first_name='Ali', last_name='Valiyev',
            date_of_birth=date(1990, 1, 1), gender='male',
            doctor=self.doc,
        )
        self.p2 = Patient.objects.create(
            first_name='Guli', last_name='Karimova',
            date_of_birth=date(1995, 5, 15), gender='female',
        )

    def test_filter_by_name(self):
        f = PatientFilter({'name': 'Ali'}, queryset=Patient.objects.all())
        self.assertEqual(f.qs.count(), 1)
        self.assertEqual(f.qs.first(), self.p1)

    def test_filter_by_gender(self):
        f = PatientFilter({'gender': 'female'}, queryset=Patient.objects.all())
        self.assertEqual(f.qs.count(), 1)
        self.assertEqual(f.qs.first(), self.p2)

    def test_filter_by_doctor(self):
        f = PatientFilter({'doctor': self.doc.pk}, queryset=Patient.objects.all())
        self.assertEqual(f.qs.count(), 1)


class DiseaseFilterTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            first_name='P', last_name='P',
            date_of_birth=date(2000, 1, 1), gender='male',
        )
        self.d1 = Disease.objects.create(
            icd_code='E11', name='Diabet', severity='severe',
            patient=self.patient, diagnosed_date=date(2024, 3, 1),
        )
        self.d2 = Disease.objects.create(
            icd_code='J06.9', name='ORVI', severity='mild',
            patient=self.patient, diagnosed_date=date(2024, 1, 10),
        )

    def test_filter_by_icd_code(self):
        f = DiseaseFilter({'icd_code': 'E11'}, queryset=Disease.objects.all())
        self.assertEqual(f.qs.count(), 1)
        self.assertEqual(f.qs.first(), self.d1)

    def test_filter_by_severity(self):
        f = DiseaseFilter({'severity': 'mild'}, queryset=Disease.objects.all())
        self.assertEqual(f.qs.count(), 1)
        self.assertEqual(f.qs.first(), self.d2)

    def test_filter_by_name(self):
        f = DiseaseFilter({'name': 'Diabet'}, queryset=Disease.objects.all())
        self.assertEqual(f.qs.count(), 1)

    def test_filter_by_patient(self):
        f = DiseaseFilter({'patient': self.patient.pk}, queryset=Disease.objects.all())
        self.assertEqual(f.qs.count(), 2)

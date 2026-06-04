from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from clinic.models import Department, Disease, Doctor, Patient, User


class DoctorAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='p', role=User.Role.ADMIN,
        )
        self.clinician = User.objects.create_user(
            username='clinician', password='p', role=User.Role.CLINICIAN,
        )
        self.reception = User.objects.create_user(
            username='reception', password='p', role=User.Role.RECEPTION,
        )
        self.doctor = Doctor.objects.create(
            first_name='Ahmad', last_name='Karimov',
            specialty='Kardiolog', department=Department.CARDIOLOGY,
        )

    def test_list_doctors_as_admin(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get('/api/doctors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_doctors_as_reception(self):
        self.client.force_authenticate(self.reception)
        response = self.client.get('/api/doctors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_doctors_unauthenticated(self):
        response = self.client.get('/api/doctors/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_doctor_as_admin(self):
        self.client.force_authenticate(self.admin)
        data = {
            'first_name': 'New', 'last_name': 'Doc',
            'specialty': 'Nevrolog', 'department': 'neurology',
        }
        response = self.client.post('/api/doctors/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Doctor.objects.count(), 2)

    def test_create_doctor_as_clinician_denied(self):
        self.client.force_authenticate(self.clinician)
        data = {
            'first_name': 'New', 'last_name': 'Doc',
            'specialty': 'Nevrolog', 'department': 'neurology',
        }
        response = self.client.post('/api/doctors/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_doctor_as_reception_denied(self):
        self.client.force_authenticate(self.reception)
        data = {
            'first_name': 'New', 'last_name': 'Doc',
            'specialty': 'Nevrolog', 'department': 'neurology',
        }
        response = self.client.post('/api/doctors/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_doctor_as_admin(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(
            f'/api/doctors/{self.doctor.pk}/',
            {'specialty': 'Updated'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_doctor_as_clinician(self):
        self.client.force_authenticate(self.clinician)
        response = self.client.patch(
            f'/api/doctors/{self.doctor.pk}/',
            {'specialty': 'Updated'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_doctor_as_admin(self):
        self.client.force_authenticate(self.admin)
        response = self.client.delete(f'/api/doctors/{self.doctor.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_doctor_as_clinician_denied(self):
        self.client.force_authenticate(self.clinician)
        response = self.client.delete(f'/api/doctors/{self.doctor.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_doctor_patients_action(self):
        self.client.force_authenticate(self.admin)
        Patient.objects.create(
            first_name='P', last_name='P',
            date_of_birth=date(2000, 1, 1), gender='male',
            doctor=self.doctor,
        )
        response = self.client.get(f'/api/doctors/{self.doctor.pk}/patients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_doctors(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get('/api/doctors/', {'search': 'Ahmad'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_doctors_by_department(self):
        self.client.force_authenticate(self.admin)
        Doctor.objects.create(
            first_name='Other', last_name='Doc',
            specialty='Nevrolog', department=Department.NEUROLOGY,
        )
        response = self.client.get('/api/doctors/', {'department': 'cardiology'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        if isinstance(results, list):
            self.assertEqual(len(results), 1)


class PatientAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='p', role=User.Role.ADMIN,
        )
        self.clinician = User.objects.create_user(
            username='clinician', password='p', role=User.Role.CLINICIAN,
        )
        self.reception = User.objects.create_user(
            username='reception', password='p', role=User.Role.RECEPTION,
        )
        self.doctor = Doctor.objects.create(
            first_name='Doc', last_name='Tor', specialty='General',
        )
        self.patient = Patient.objects.create(
            first_name='Sardor', last_name='Toshmatov',
            date_of_birth=date(1995, 3, 20), gender='male',
            doctor=self.doctor,
        )

    def test_list_patients_as_clinician(self):
        self.client.force_authenticate(self.clinician)
        response = self.client.get('/api/patients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_patient_profile(self):
        self.client.force_authenticate(self.admin)
        Disease.objects.create(
            icd_code='E11', name='Diabet', patient=self.patient,
            diagnosed_date=date(2024, 3, 1),
        )
        response = self.client.get(f'/api/patients/{self.patient.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('diseases', response.data)

    def test_create_patient_as_reception(self):
        self.client.force_authenticate(self.reception)
        data = {
            'first_name': 'New', 'last_name': 'Patient',
            'date_of_birth': '2000-01-01', 'gender': 'female',
            'doctor': self.doctor.pk,
        }
        response = self.client.post('/api/patients/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_patient_as_reception_denied(self):
        self.client.force_authenticate(self.reception)
        response = self.client.delete(f'/api/patients/{self.patient.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_patient_as_admin(self):
        self.client.force_authenticate(self.admin)
        response = self.client.delete(f'/api/patients/{self.patient.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_patient_as_clinician(self):
        self.client.force_authenticate(self.clinician)
        response = self.client.patch(
            f'/api/patients/{self.patient.pk}/',
            {'first_name': 'Updated'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patient_diseases_action(self):
        self.client.force_authenticate(self.admin)
        Disease.objects.create(
            icd_code='J06.9', name='ORVI', patient=self.patient,
            diagnosed_date=date(2024, 1, 10),
        )
        response = self.client.get(f'/api/patients/{self.patient.pk}/diseases/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class DiseaseAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='p', role=User.Role.ADMIN,
        )
        self.clinician = User.objects.create_user(
            username='clinician', password='p', role=User.Role.CLINICIAN,
        )
        self.reception = User.objects.create_user(
            username='reception', password='p', role=User.Role.RECEPTION,
        )
        self.patient = Patient.objects.create(
            first_name='P', last_name='P',
            date_of_birth=date(2000, 1, 1), gender='male',
        )
        self.disease = Disease.objects.create(
            icd_code='E11', name='Diabet', severity='severe',
            patient=self.patient, diagnosed_date=date(2024, 3, 1),
        )

    def test_list_diseases_as_clinician(self):
        self.client.force_authenticate(self.clinician)
        response = self.client.get('/api/diseases/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_disease_as_admin(self):
        self.client.force_authenticate(self.admin)
        data = {
            'icd_code': 'J00', 'name': 'Shamollash',
            'severity': 'mild', 'patient': self.patient.pk,
            'diagnosed_date': '2024-04-01',
        }
        response = self.client.post('/api/diseases/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_disease_as_clinician_denied(self):
        self.client.force_authenticate(self.clinician)
        data = {
            'icd_code': 'J00', 'name': 'Shamollash',
            'severity': 'mild', 'patient': self.patient.pk,
            'diagnosed_date': '2024-04-01',
        }
        response = self.client.post('/api/diseases/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_disease_as_clinician(self):
        self.client.force_authenticate(self.clinician)
        response = self.client.patch(
            f'/api/diseases/{self.disease.pk}/',
            {'notes': 'Updated notes'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_disease_as_admin(self):
        self.client.force_authenticate(self.admin)
        response = self.client.delete(f'/api/diseases/{self.disease.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_disease_as_clinician_denied(self):
        self.client.force_authenticate(self.clinician)
        response = self.client.delete(f'/api/diseases/{self.disease.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_diseases_as_reception_denied(self):
        self.client.force_authenticate(self.reception)
        response = self.client.get('/api/diseases/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_search_diseases(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get('/api/diseases/', {'search': 'E11'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

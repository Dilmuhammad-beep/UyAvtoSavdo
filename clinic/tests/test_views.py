from datetime import date

from django.test import TestCase
from django.urls import reverse

from clinic.models import Department, Disease, Doctor, Patient, User


class AuthViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', role=User.Role.ADMIN,
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CareTrack')

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser', 'password': 'testpass123',
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_failure(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser', 'password': 'wrong',
        })
        self.assertEqual(response.status_code, 200)

    def test_login_redirect_if_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin', password='p', role=User.Role.ADMIN,
        )
        self.client.login(username='admin', password='p')

    def test_dashboard_loads(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Boshqaruv paneli')

    def test_dashboard_counts(self):
        Doctor.objects.create(first_name='D', last_name='D', specialty='S')
        Patient.objects.create(
            first_name='P', last_name='P',
            date_of_birth=date(2000, 1, 1), gender='male',
        )
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, '1')  # counts appear


class DoctorListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin', password='p', role=User.Role.ADMIN,
        )
        self.client.login(username='admin', password='p')
        self.doc = Doctor.objects.create(
            first_name='Ahmad', last_name='Karimov',
            specialty='Kardiolog', department=Department.CARDIOLOGY,
        )

    def test_doctor_list_loads(self):
        response = self.client.get(reverse('doctor-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ahmad')

    def test_doctor_search(self):
        Doctor.objects.create(first_name='Zafar', last_name='Olimov', specialty='Nevrolog')
        response = self.client.get(reverse('doctor-list'), {'q': 'Zafar'})
        self.assertContains(response, 'Zafar')
        self.assertNotContains(response, 'Ahmad')

    def test_doctor_filter_department(self):
        Doctor.objects.create(
            first_name='Other', last_name='Doc',
            specialty='Nevrolog', department=Department.NEUROLOGY,
        )
        response = self.client.get(reverse('doctor-list'), {'department': 'cardiology'})
        self.assertContains(response, 'Ahmad')
        self.assertNotContains(response, 'Other')


class PatientListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin', password='p', role=User.Role.ADMIN,
        )
        self.client.login(username='admin', password='p')
        self.patient = Patient.objects.create(
            first_name='Sardor', last_name='Toshmatov',
            date_of_birth=date(1995, 3, 20), gender='male',
        )

    def test_patient_list_loads(self):
        response = self.client.get(reverse('patient-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sardor')

    def test_patient_search(self):
        Patient.objects.create(
            first_name='Aziza', last_name='Nurmatova',
            date_of_birth=date(2000, 1, 1), gender='female',
        )
        response = self.client.get(reverse('patient-list'), {'q': 'Aziza'})
        self.assertContains(response, 'Aziza')
        self.assertNotContains(response, 'Sardor')


class PatientProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin', password='p', role=User.Role.ADMIN,
        )
        self.client.login(username='admin', password='p')
        self.doctor = Doctor.objects.create(
            first_name='Doc', last_name='Tor', specialty='General',
        )
        self.patient = Patient.objects.create(
            first_name='Sardor', last_name='Toshmatov',
            date_of_birth=date(1995, 3, 20), gender='male',
            doctor=self.doctor,
        )
        self.disease = Disease.objects.create(
            icd_code='E11', name='Diabet', severity='severe',
            patient=self.patient, diagnosed_date=date(2024, 3, 1),
        )

    def test_profile_loads(self):
        response = self.client.get(reverse('patient-profile', args=[self.patient.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sardor')
        self.assertContains(response, 'Doc')
        self.assertContains(response, 'E11')

    def test_profile_shows_diseases(self):
        response = self.client.get(reverse('patient-profile', args=[self.patient.pk]))
        self.assertContains(response, 'Diabet')
        self.assertContains(response, 'E11')


class DiseaseListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin', password='p', role=User.Role.ADMIN,
        )
        self.client.login(username='admin', password='p')
        self.patient = Patient.objects.create(
            first_name='P', last_name='P',
            date_of_birth=date(2000, 1, 1), gender='male',
        )
        self.disease = Disease.objects.create(
            icd_code='J06.9', name='ORVI', severity='mild',
            patient=self.patient, diagnosed_date=date(2024, 1, 10),
        )

    def test_disease_list_loads(self):
        response = self.client.get(reverse('disease-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ORVI')

    def test_disease_search(self):
        Disease.objects.create(
            icd_code='I10', name='Gipertoniya', severity='moderate',
            patient=self.patient, diagnosed_date=date(2024, 2, 1),
        )
        response = self.client.get(reverse('disease-list'), {'q': 'Gipertoniya'})
        self.assertContains(response, 'Gipertoniya')
        self.assertNotContains(response, 'ORVI')

    def test_disease_filter_severity(self):
        Disease.objects.create(
            icd_code='I10', name='Gipertoniya', severity='severe',
            patient=self.patient, diagnosed_date=date(2024, 2, 1),
        )
        response = self.client.get(reverse('disease-list'), {'severity': 'mild'})
        self.assertContains(response, 'ORVI')
        self.assertNotContains(response, 'Gipertoniya')

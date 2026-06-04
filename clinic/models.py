from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with role-based access."""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        CLINICIAN = 'clinician', 'Klinitsist'
        RECEPTION = 'reception', 'Qabulxona xodimi'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.RECEPTION,
    )

    class Meta:
        ordering = ['username']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_clinician(self):
        return self.role == self.Role.CLINICIAN

    @property
    def is_reception(self):
        return self.role == self.Role.RECEPTION


class Department(models.TextChoices):
    GENERAL = 'general', 'Umumiy amaliyot'
    CARDIOLOGY = 'cardiology', 'Kardiologiya'
    NEUROLOGY = 'neurology', 'Nevrologiya'
    DERMATOLOGY = 'dermatology', 'Dermatologiya'
    ORTHOPEDICS = 'orthopedics', 'Ortopediya'
    DIAGNOSTICS = 'diagnostics', 'Diagnostika'
    EMERGENCY = 'emergency', 'Favqulodda yordam'


class Doctor(models.Model):
    """Shifokor profili."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=200)
    department = models.CharField(
        max_length=30,
        choices=Department.choices,
        default=Department.GENERAL,
    )
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} — {self.get_department_display()}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def patient_count(self):
        return self.patients.count()


class Patient(models.Model):
    """Bemor yozuvi."""

    class Gender(models.TextChoices):
        MALE = 'male', 'Erkak'
        FEMALE = 'female', 'Ayol'

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=Gender.choices)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        related_name='patients',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def diagnosis_count(self):
        return self.diseases.count()


class Disease(models.Model):
    """Kasallik / Tashxis yozuvi."""

    class Severity(models.TextChoices):
        MILD = 'mild', 'Yengil'
        MODERATE = 'moderate', "O'rtacha"
        SEVERE = 'severe', 'Og\'ir'
        CRITICAL = 'critical', 'Juda og\'ir'

    icd_code = models.CharField(max_length=10, help_text='ICD-10 kodi')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    severity = models.CharField(
        max_length=10,
        choices=Severity.choices,
        default=Severity.MODERATE,
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='diseases',
    )
    diagnosed_date = models.DateField()
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-diagnosed_date']
        verbose_name_plural = 'diseases'

    def __str__(self):
        return f"{self.icd_code} — {self.name} ({self.get_severity_display()})"

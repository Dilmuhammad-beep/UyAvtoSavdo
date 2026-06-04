from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from clinic.models import Disease, Doctor, Patient, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'specialty', 'department', 'phone', 'is_active']
    list_filter = ['department', 'is_active']
    search_fields = ['first_name', 'last_name', 'specialty']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'date_of_birth', 'gender', 'doctor', 'is_active']
    list_filter = ['gender', 'is_active', 'doctor']
    search_fields = ['first_name', 'last_name', 'phone', 'email']


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ['icd_code', 'name', 'severity', 'patient', 'diagnosed_date', 'is_active']
    list_filter = ['severity', 'is_active']
    search_fields = ['icd_code', 'name', 'description']

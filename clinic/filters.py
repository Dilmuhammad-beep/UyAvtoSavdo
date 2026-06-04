import django_filters

from clinic.models import Disease, Doctor, Patient


class DoctorFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='filter_name')
    department = django_filters.CharFilter(field_name='department')
    specialty = django_filters.CharFilter(field_name='specialty', lookup_expr='icontains')
    is_active = django_filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = Doctor
        fields = ['department', 'specialty', 'is_active']

    def filter_name(self, queryset, name, value):
        return queryset.filter(
            models_Q_first_or_last(value)
        )


def models_Q_first_or_last(value):
    from django.db.models import Q
    return Q(first_name__icontains=value) | Q(last_name__icontains=value)


class PatientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='filter_name')
    doctor = django_filters.NumberFilter(field_name='doctor__id')
    gender = django_filters.CharFilter(field_name='gender')
    is_active = django_filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = Patient
        fields = ['doctor', 'gender', 'is_active']

    def filter_name(self, queryset, name, value):
        return queryset.filter(models_Q_first_or_last(value))


class DiseaseFilter(django_filters.FilterSet):
    icd_code = django_filters.CharFilter(field_name='icd_code', lookup_expr='icontains')
    severity = django_filters.CharFilter(field_name='severity')
    patient = django_filters.NumberFilter(field_name='patient__id')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    is_active = django_filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = Disease
        fields = ['icd_code', 'severity', 'patient', 'name', 'is_active']

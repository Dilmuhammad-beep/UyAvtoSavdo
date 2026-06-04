from django.urls import include, path
from rest_framework.routers import DefaultRouter

from clinic import views

router = DefaultRouter()
router.register(r'doctors', views.DoctorViewSet)
router.register(r'patients', views.PatientViewSet)
router.register(r'diseases', views.DiseaseViewSet)

urlpatterns = [
    # API
    path('api/', include(router.urls)),

    # Template views
    path('', views.dashboard_view, name='dashboard'),
    path('doctors/', views.doctor_list_view, name='doctor-list'),
    path('patients/', views.patient_list_view, name='patient-list'),
    path('patients/<int:pk>/', views.patient_profile_view, name='patient-profile'),
    path('diseases/', views.disease_list_view, name='disease-list'),

    # Auth
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
]

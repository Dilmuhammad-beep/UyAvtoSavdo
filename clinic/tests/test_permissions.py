from django.test import RequestFactory, TestCase

from clinic.models import User
from clinic.permissions import IsAdminRole, IsClinicianOrAdmin, IsReceptionOrAbove


class PermissionTestMixin:
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = User.objects.create_user(
            username='admin', password='p', role=User.Role.ADMIN,
        )
        self.clinician = User.objects.create_user(
            username='clinician', password='p', role=User.Role.CLINICIAN,
        )
        self.reception = User.objects.create_user(
            username='reception', password='p', role=User.Role.RECEPTION,
        )

    def _make_request(self, method, user):
        request = getattr(self.factory, method)('/')
        request.user = user
        return request


class IsAdminRoleTests(PermissionTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.perm = IsAdminRole()

    def test_admin_has_permission(self):
        request = self._make_request('get', self.admin)
        self.assertTrue(self.perm.has_permission(request, None))

    def test_clinician_denied(self):
        request = self._make_request('get', self.clinician)
        self.assertFalse(self.perm.has_permission(request, None))

    def test_reception_denied(self):
        request = self._make_request('get', self.reception)
        self.assertFalse(self.perm.has_permission(request, None))

    def test_anonymous_denied(self):
        from django.contrib.auth.models import AnonymousUser
        request = self._make_request('get', AnonymousUser())
        self.assertFalse(self.perm.has_permission(request, None))


class IsClinicianOrAdminTests(PermissionTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.perm = IsClinicianOrAdmin()

    def test_admin_all_methods(self):
        for method in ('get', 'post', 'put', 'patch', 'delete'):
            request = self._make_request(method, self.admin)
            self.assertTrue(self.perm.has_permission(request, None))

    def test_clinician_get_allowed(self):
        request = self._make_request('get', self.clinician)
        self.assertTrue(self.perm.has_permission(request, None))

    def test_clinician_put_allowed(self):
        request = self._make_request('put', self.clinician)
        self.assertTrue(self.perm.has_permission(request, None))

    def test_clinician_patch_allowed(self):
        request = self._make_request('patch', self.clinician)
        self.assertTrue(self.perm.has_permission(request, None))

    def test_clinician_post_denied(self):
        request = self._make_request('post', self.clinician)
        self.assertFalse(self.perm.has_permission(request, None))

    def test_clinician_delete_denied(self):
        request = self._make_request('delete', self.clinician)
        self.assertFalse(self.perm.has_permission(request, None))

    def test_reception_denied(self):
        request = self._make_request('get', self.reception)
        self.assertFalse(self.perm.has_permission(request, None))


class IsReceptionOrAboveTests(PermissionTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.perm = IsReceptionOrAbove()

    def test_admin_allowed(self):
        request = self._make_request('get', self.admin)
        self.assertTrue(self.perm.has_permission(request, None))

    def test_clinician_allowed(self):
        request = self._make_request('get', self.clinician)
        self.assertTrue(self.perm.has_permission(request, None))

    def test_reception_allowed(self):
        request = self._make_request('get', self.reception)
        self.assertTrue(self.perm.has_permission(request, None))

    def test_anonymous_denied(self):
        from django.contrib.auth.models import AnonymousUser
        request = self._make_request('get', AnonymousUser())
        self.assertFalse(self.perm.has_permission(request, None))

    def test_object_permission_admin_full(self):
        request = self._make_request('delete', self.admin)
        self.assertTrue(self.perm.has_object_permission(request, None, None))

    def test_object_permission_clinician_get(self):
        request = self._make_request('get', self.clinician)
        self.assertTrue(self.perm.has_object_permission(request, None, None))

    def test_object_permission_clinician_delete_denied(self):
        request = self._make_request('delete', self.clinician)
        self.assertFalse(self.perm.has_object_permission(request, None, None))

    def test_object_permission_reception_get(self):
        request = self._make_request('get', self.reception)
        self.assertTrue(self.perm.has_object_permission(request, None, None))

    def test_object_permission_reception_post(self):
        request = self._make_request('post', self.reception)
        self.assertTrue(self.perm.has_object_permission(request, None, None))

    def test_object_permission_reception_delete_denied(self):
        request = self._make_request('delete', self.reception)
        self.assertFalse(self.perm.has_object_permission(request, None, None))

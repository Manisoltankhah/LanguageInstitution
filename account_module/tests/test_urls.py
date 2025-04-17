from django.test import SimpleTestCase
from django.urls import reverse, resolve
from account_module.views import (
    UserRegistrationView,
    TeacherGatewayView,
    StudentGatewayView
)

class SimpleURLTests(SimpleTestCase):
    def test_register_url(self):
        url = reverse('register')
        self.assertEqual(url, '/register/')
        self.assertEqual(
            resolve(url).func.view_class,
            UserRegistrationView
        )

    def test_teacher_gateway_url(self):
        url = reverse('teacher-gateway')
        self.assertEqual(url, '/teacher-gateway/')
        self.assertEqual(
            resolve(url).func.view_class,
            TeacherGatewayView
        )

    def test_student_gateway_url(self):
        url = reverse('student-gateway')
        self.assertEqual(url, '/student-gateway/')
        self.assertEqual(
            resolve(url).func.view_class,
            StudentGatewayView
        )
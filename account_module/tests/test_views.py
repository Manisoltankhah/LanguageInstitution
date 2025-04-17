from django.test import TestCase, Client
from django.urls import reverse
from account_module.models import User, Term
from django.contrib.auth import authenticate


class TestViews(TestCase):
    def setUp(self):
        """
        Set up initial data for testing.
        """
        self.client = Client()

        # Create a term for testing
        self.term = Term.objects.create(name="Term 1", order=1)

        # Create a teacher for testing
        self.teacher = User.objects.create_user(
            username="teacher1",
            password="password123",
            user_type="teacher",
            current_term=self.term,
            national_id="1234567890",  # Add a valid national_id
        )

        # Create a student for testing
        self.student = User.objects.create_user(
            username="student1",
            password="password123",
            user_type="student",
            current_term=self.term,
            national_id="0987654321",  # Add a valid national_id
        )

    def test_user_registration_view_get(self):
        """
        Test the GET request for UserRegistrationView.
        """
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIn('form', response.context)

    def test_user_registration_view_post_valid(self):
        """
        Test the POST request for UserRegistrationView with valid data.
        """
        term = Term.objects.create(name="Test Term", order=1)  # Create a term for testing
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'user_type': 'student',  # Ensure this matches the choices in USER_TYPE_CHOICES
            'gender': 'male',  # Ensure this matches the choices in GENDER_CHOICES
            'national_id': '1234567891',  # Add a valid national_id
            'parent_number': '09123456789',  # Add a valid parent number
            'password': 'securepassword123',  # Add a valid password
            'confirm_password': 'securepassword123',  # Confirm the password
        }
        response = self.client.post(reverse('register'), data)
        if response.status_code != 302:  # Debugging: Print form errors if validation fails
            form = response.context['form']
            print(form.errors)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='1234567890').exists())  # Check if the user was created

    def test_user_registration_view_post_invalid(self):
        """
        Test the POST request for UserRegistrationView with invalid data.
        """
        data = {
            'username': 'newuser',
            'password1': 'short',
            'password2': 'short',  # Password too short
            'user_type': 'student',
            'current_term': self.term.id,
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)  # Form errors should re-render the page
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_student_gateway_view_get(self):
        """
        Test the GET request for StudentGatewayView.
        """
        response = self.client.get(reverse('student-gateway'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_gateway.html')
        self.assertIn('student_gateway_form', response.context)

    def test_student_gateway_view_post_valid(self):
        """
        Test the POST request for StudentGatewayView with valid credentials.
        """
        data = {
            'username': '0987654321',  # Add a valid national_id
            'password': 'password123',  # Add a valid password
        }
        response = self.client.post(reverse('student-gateway'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        self.assertRedirects(response, reverse('student_panel', args=[self.student.slug]))

    def test_student_gateway_view_post_invalid_credentials(self):
        """
        Test the POST request for StudentGatewayView with invalid credentials.
        """
        data = {
            'username': 'student1',
            'password': 'wrongpassword',
        }
        response = self.client.post(reverse('student-gateway'), data)
        self.assertEqual(response.status_code, 200)  # Form errors should re-render the page
        self.assertContains(response, 'نام کاربری و رمز عبور اشتباه است')

    def test_teacher_gateway_view_get(self):
        """
        Test the GET request for TeacherGatewayView.
        """
        response = self.client.get(reverse('teacher-gateway'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teacher_gateway.html')
        self.assertIn('teachers_gateway_form', response.context)

    def test_teacher_gateway_view_post_valid(self):
        """
        Test the POST request for TeacherGatewayView with valid credentials.
        """
        data = {
            'username': '1234567890',
            'password': 'password123',
        }
        response = self.client.post(reverse('teacher-gateway'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        self.assertRedirects(response, reverse('teacher_panel', args=[self.teacher.slug]))

    def test_teacher_gateway_view_post_invalid_credentials(self):
        """
        Test the POST request for TeacherGatewayView with invalid credentials.
        """
        data = {
            'username': 'teacher1',
            'password': 'wrongpassword',
        }
        response = self.client.post(reverse('teacher-gateway'), data)
        self.assertEqual(response.status_code, 200)  # Form errors should re-render the page
        self.assertContains(response, 'نام کاربری و رمز عبور اشتباه است')

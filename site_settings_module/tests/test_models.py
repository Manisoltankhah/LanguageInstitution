from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from site_settings_module.models import SiteSettings
import os
from django.conf import settings
from django.core.exceptions import ValidationError


class SiteSettingsModelTest(TestCase):
    def setUp(self):
        # Create a test logo file
        self.logo_file = SimpleUploadedFile(
            name='test_logo.png',
            content=b'simple logo content',
            content_type='image/png'
        )

        # Create a sample site setting
        self.site_settings = SiteSettings.objects.create(
            site_name='Test School',
            logo=self.logo_file,
            about_us='This is a test school',
            rules='1. Be kind\n2. Work hard',
            address='123 Test Street, Test City',
            phone_number='09123456789',
            email='test@school.edu'
        )

    def tearDown(self):
        # Clean up the uploaded logo file
        if self.site_settings.logo and os.path.exists(self.site_settings.logo.path):
            os.remove(self.site_settings.logo.path)

    def test_site_settings_creation(self):
        """Test that SiteSettings can be created with all fields"""
        self.assertEqual(SiteSettings.objects.count(), 1)
        settings = SiteSettings.objects.first()
        self.assertEqual(settings.site_name, 'Test School')
        self.assertEqual(settings.about_us, 'This is a test school')
        self.assertEqual(settings.rules, '1. Be kind\n2. Work hard')
        self.assertEqual(settings.address, '123 Test Street, Test City')
        self.assertEqual(settings.phone_number, '09123456789')
        self.assertEqual(settings.email, 'test@school.edu')
        self.assertTrue('uploads/logo' in settings.logo.name)

    def test_optional_email_field(self):
        """Test that email field can be blank"""
        settings = SiteSettings.objects.create(
            site_name='School Without Email',
            logo=self.logo_file,
            about_us='No email',
            rules='No rules',
            address='No address',
            phone_number='09000000000',
            email=''
        )
        self.assertEqual(settings.email, '')

    def test_string_representation(self):
        """Test the __str__ method"""
        self.assertEqual(
            str(self.site_settings),
            'Test School/09123456789'
        )

    def test_logo_upload_path(self):
        """Test that logo is uploaded to the correct path"""
        # Modified to just check if 'uploads/logo' is in the path
        self.assertIn('uploads/logo', self.site_settings.logo.name)

    def test_phone_number_max_length(self):
        """Test phone_number field max length constraint"""
        field = SiteSettings._meta.get_field('phone_number')
        self.assertEqual(field.max_length, 11)

    def test_site_name_max_length(self):
        """Test site_name field max length constraint"""
        field = SiteSettings._meta.get_field('site_name')
        self.assertEqual(field.max_length, 100)

    def test_address_max_length(self):
        """Test address field max length constraint"""
        field = SiteSettings._meta.get_field('address')
        self.assertEqual(field.max_length, 500)

    def test_required_fields(self):
        """Test that required fields cannot be blank"""
        with self.assertRaises(ValidationError):
            settings = SiteSettings(
                site_name='',
                logo=None,
                about_us='',
                rules='',
                address='',
                phone_number=''
            )
            settings.full_clean()  # This will trigger validation
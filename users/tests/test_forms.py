from django.test import TestCase
from users.models import CustomUser
from users.forms import CustomUserCreationForm

class CustomUserCreationFormTests(TestCase):
    
    def test_custom_user_creation_form_valid(self):
        form_data = {
            'userId': 'testuser',
            'firstName': 'Test',
            'lastName': 'User',
            'email': 'testuser@example.com',
            'phone': '1234567890',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_custom_user_creation_form_invalid(self):
        form_data = {
            'userId': '',
            'firstName': 'Test',
            'lastName': 'User',
            'email': 'testuser@example.com',
            'phone': '1234567890',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

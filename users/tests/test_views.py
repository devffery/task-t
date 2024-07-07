from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from users.models import CustomUser, Organisation
from rest_framework_simplejwt.tokens import RefreshToken
import uuid


class UserViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='dummy_username',
            userId=str(uuid.uuid4()),
            firstName='John',
            lastName='Doe',
            email='john.doe@example.com',
            phone='1234567890',
            password='ComplexPass123!'
        )
        self.org = Organisation.objects.create(
            userId=str(uuid.uuid4()),
            name='Test Organisation',
            description='A test organisation'
        )
        self.org.users.add(self.user)
        self.valid_user_data = {
            'userId': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
            'firstName': 'Jane',
            'lastName': 'Smith',
            'email': 'jane.smith@example.com',
            'phone': '0987654321',
            'password1': 'AnotherPass123!',
            'password2': 'AnotherPass123!',
        }
        self.invalid_user_data = {
            'userId': '',
            'firstName': '',
            'lastName': 'Smith',
            'email': 'jane.smith@example.com',
            'phone': '0987654321',
            'password1': 'AnotherPass123!',
            'password2': 'AnotherPass123!',
        }
        self.login_data = {
            'email': 'john.doe@example.com',
            'password': 'ComplexPass123!',
        }

    def test_register_view(self):
        url = reverse('register')
        response = self.client.post(url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('accessToken', response.data['data'])

        response = self.client.post(url, self.invalid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_login_view(self):
        url = reverse('login')
        response = self.client.post(url, self.login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('accessToken', response.data['data'])

        response = self.client.post(url, {'email': 'invalid@example.com', 'password': 'wrongpass'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_view(self):
        url = reverse('get_user', args=[self.user.userId])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['userId'], self.user.userId)

        other_user = CustomUser.objects.create_user(
            userId=str(uuid.uuid4()),
            firstName='Other',
            lastName='User',
            email='other.user@example.com',
            phone='1231231234',
            password='Pass123!'
        )
        url = reverse('get_user', args=[other_user.userId])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_organisation_view(self):
        url = reverse('get_organisations')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)

        response = self.client.post(url, {'name': 'New Org', 'description': 'A new organisation'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['name'], 'New Org')

    def test_get_organisation_by_id_view(self):
        url = reverse('get_organisation', args=[self.org.orgId])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['orgId'], self.org.orgId)

    def test_add_user_to_organisation_view(self):
        other_user = CustomUser.objects.create_user(
            userId=str(uuid.uuid4()),
            firstName='Other',
            lastName='User',
            email='other.user@example.com',
            phone='1231231234',
            password='Pass123!'
        )
        url = reverse('add_user_to_organisation', args=[self.org.orgId])
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, {'userId': other_user.userId}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.org.users.filter(userId=other_user.userId).exists())

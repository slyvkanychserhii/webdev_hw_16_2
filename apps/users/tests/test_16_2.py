from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from apps.users.models import User
from apps.users.serializers.user_serializers import UserListSerializer
from unittest.mock import patch


class UserAPITestCase(APITestCase):
    fixtures = ['apps/users/tests/users_fixture.json']

    def setUp(self):
        self.client = APIClient()
        self.user_list_url = reverse('user-list')
        self.register_url = reverse('user-register')
        self.user_detail_url = lambda pk: reverse('user-detail', kwargs={'pk': pk})

    # 1
    def test_get_all_users(self):
        '''
        Проверка получения списка всех пользователей
        '''
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        users = User.objects.all()
        serializer = UserListSerializer(users, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_get_users_by_project_name(self):
        '''
        Проверка получения списка всех пользователей по имени проекта
        '''
        project_name = 'Project 1'
        url = reverse('user-list')
        response = self.client.get(url, {'project_name': project_name})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        # print('>>>>>', response.data, '>>>>>', sep='\n')
        for user_data in response.data:
            self.assertEqual(user_data['project'], project_name)

    @patch('apps.users.views.user_views.UserListGenericView.get_queryset')
    def test_get_empty_user_list(self, mock_get_queryset):
        '''
        Проверка получения пустого списка пользователей(нужно подменить выходной QuerySet)
        '''
        mock_get_queryset.return_value = User.objects.none()
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, [])

    def test_user_list_serializer(self):
        '''
        Проверка работы сериализатора на правильное отображение данных списка пользователей
        '''
        users = User.objects.all()
        serializer = UserListSerializer(users, many=True)
        serialized_data = serializer.data
        for user_data, user in zip(serialized_data, users):
            self.assertEqual(user_data['first_name'], user.first_name)
            self.assertEqual(user_data['last_name'], user.last_name)
            self.assertEqual(user_data['email'], user.email)
            self.assertEqual(user_data['phone'], user.phone)
            self.assertEqual(user_data['last_login'], user.last_login)
            self.assertEqual(user_data['position'], user.position)

    def test_get_user_detail(self):
        '''
        Проверка получения деталей конкретного пользователя по его ID.
        '''
        user_id = 1
        response = self.client.get(self.user_detail_url(user_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'serhiislyvkanych')

    # 2
    def test_create_user(self):
        '''
        Проверка создания нового пользователя с хорошими данными
        '''
        data = {
            'username': 'albinaslyvkanych',
            'first_name': 'Albina',
            'last_name': 'Slyvkanych',
            'email': 'albinaslyvkanych@example.com',
            'position': 'PROGRAMMER',
            'password': 'StrongPassword123',
            're_password': 'StrongPassword123'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='albinaslyvkanych').exists())

    def test_create_user_with_invalid_data(self):
        '''
        Проверка создания нового пользователя с испорченными данными
        '''
        data = {
            'username': 'maksym slyvkanych',
            'first_name': 'Maksym',
            'last_name': 'Slyvkanych',
            'email': 'maksymslyvkanych@example',
            'position': 'QA',
            'password': 'pass',
            're_password': 'pass'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_missing_data(self):
        '''
        Проверка создания нового пользователя с пропуском обязательных данных
        '''
        url = reverse('user-register')  # Маршрут для создания нового пользователя
        data = {
            "username": "alisaslyvkanych",
            "first_name": "Alisa",
            # last_name отсутствует
            "email": "alisaslyvkanych@example.com",
            "position": "PROGRAMMER",
            "password": "TestPassword123",
            "re_password": "TestPassword123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('last_name', response.data)

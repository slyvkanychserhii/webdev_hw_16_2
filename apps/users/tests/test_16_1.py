from django.test import TestCase
from apps.users.models import User
from apps.users.serializers.user_serializers import RegisterUserSerializer
from apps.users.choices.positions import Positions
from apps.projects.models import Project


# Задача 1.1 Напишите тесты для API запросов на проверку реализованных методов:
class UserListGenericViewTestCase(TestCase):
    # - Получение списка всех пользователей
    def test_user_list(self):
        User.objects.bulk_create([
            User(username='joelouis', email='joelouis@gmail.com'),
            User(username='mannypacquiao', email='mannypacquiao@gmail.com'),
            User(username='jackdempsey', email='jackdempsey'),
        ])

        response = self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 3)


class RegisterUserGenericViewTestCase(TestCase):
    def setUp(self):
        self.url = '/api/v1/users/register/'
        self.data = {
            'username': 'joelouis',
            'first_name': 'Joe',
            'last_name': 'Louis',
            'email': 'joelouis@gmail.com',
            'position': 'CEO',
            'password': ',123456qwerty',
            're_password': ',123456qwerty'
        }

    # - Регистрация нового пользователя
    def test_user_register(self):
        response = self.client.post(self.url, self.data)
        print(response)
        self.assertEqual(response.status_code, 201)
        self.assertIsInstance(response.data, dict)
        self.assertEqual(User.objects.count(), 1)

    def test_user_register_invalid_email(self):
        self.data['email'] = 'joelouis'
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)

    def test_user_register_invalid_position(self):
        self.data['position'] = 'BOSS'
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 400)

    def test_user_register_password_mismatch(self):
        self.data['re_password'] = 'qwerty123456,'
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 400)


# Задача 1.2 Напишите тесты на проверку валидации данных при следующих условиях:
class RegisterUserSerializerTestCase(TestCase):
    def setUp(self):
        self.data = {
            'username': 'joelouis',
            'first_name': 'Joe',
            'last_name': 'Louis',
            'email': 'joelouis@gmail.com',
            'position': Positions.CEO,
            'password': ',123456qwerty',
            're_password': ',123456qwerty'
        }

    # - регистрация нового пользователя
    def test_valid_user_data(self):
        serializer = RegisterUserSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIsInstance(serializer.validated_data['username'], str)
        self.assertIsInstance(serializer.validated_data['first_name'], str)
        self.assertIsInstance(serializer.validated_data['last_name'], str)
        self.assertIsInstance(serializer.validated_data['email'], str)
        self.assertIsInstance(serializer.validated_data['position'], str)
        self.assertIsInstance(serializer.validated_data['password'], str)
        self.assertIsInstance(serializer.validated_data['re_password'], str)

    # проверку возможных ошибок валидации
    def test_valid_username(self):
        self.data['username'] = 'joe.louis'
        serializer = RegisterUserSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            'The username must be alphanumeric characters or have only _ symbol',
            [str(i) for i in serializer.errors['non_field_errors']])

    def test_valid_first_name(self):
        self.data['first_name'] = 'Joe1'
        serializer = RegisterUserSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            'The first name must contain only alphabet symbols',
            [str(i) for i in serializer.errors['non_field_errors']])

    def test_valid_last_name(self):
        self.data['last_name'] = 'Louis1'
        serializer = RegisterUserSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            'The last name must contain only alphabet symbols',
            [str(i) for i in serializer.errors['non_field_errors']])

    def test_valid_password(self):
        self.data['re_password'] = 'qwerty123456,'
        serializer = RegisterUserSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
        self.assertEqual(serializer.errors['password'][0], 'Passwords don\'t match')


# Задача 2. Написание кода для объекта пользователя через BDD + TDD
# На основе составленного вами сценария напишите тесты для:
class UserDetailGenericViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='joelouis',
            first_name='Joe',
            last_name='Louis',
            email='joelouis@gmail.com',
            phone='1234567890',
            position='CEO',
            project=Project.objects.create(name='Project1')
        )

    # - получения информации об определённом пользователе.
    # - ожидаемых полях и их типах данных.
    def test_user_detail_success(self):
        response = self.client.get(f'/api/v1/users/{self.user.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data['username'], str)
        self.assertIsInstance(response.data['first_name'], str)
        self.assertIsInstance(response.data['last_name'], str)
        self.assertIsInstance(response.data['email'], str)
        self.assertIsInstance(response.data['phone'], str)
        self.assertIsInstance(response.data['position'], str)
        self.assertIsInstance(response.data['project'], str)

        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['first_name'], self.user.first_name)
        self.assertEqual(response.data['last_name'], self.user.last_name)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['phone'], self.user.phone)
        self.assertEqual(response.data['position'], self.user.position)
        self.assertEqual(response.data['project'], self.user.project.name)

    # - проверьте случай, если был передан несуществующий id.
    def test_user_detail_not_found(self):
        response = self.client.get('/api/v1/users/999/')
        self.assertEqual(response.status_code, 404)
        self.assertIn('detail', response.data)

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_url_pages_in_its_location(self):
        """Тест URL страниц приложения Users."""
        pages_url_names = {
            '/auth/signup/': HTTPStatus.OK.value,
            '/auth/login/': HTTPStatus.OK.value,
            '/auth/logout/': HTTPStatus.OK.value,
            '/auth/password_change/': HTTPStatus.FOUND.value,
            '/auth/password_change/done/': HTTPStatus.FOUND.value,
            '/auth/password_reset/': HTTPStatus.OK.value,
            '/auth/password_reset/done/': HTTPStatus.OK.value,
            '/auth/reset/<uidb64>/<token>/': HTTPStatus.OK.value,
            '/auth/reset/done/': HTTPStatus.OK.value,
        }
        for address, code in pages_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_users_urls_available_for_authorized(self):
        """
        HTTPStatus.OK (200) - Страницы доступны авторизированному пользователю.
        HTTPStatus.FOUND (302) - Страницы доступны только для автора
        """
        pages_url_names = {
            '/auth/password_change/': HTTPStatus.OK.value,
            '/auth/password_change/done/': HTTPStatus.OK.value,
        }
        for address, code in pages_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, code)


class UsersViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_pages_accessible_by_name(self):
        """Тест names страниц приложения Users."""
        pages_names = {
            reverse('users:signup'): HTTPStatus.OK.value,
            reverse('users:logout'): HTTPStatus.OK.value,
            reverse('users:login'): HTTPStatus.OK.value,
            reverse('users:password_change_form'): HTTPStatus.FOUND.value,
            reverse('users:password_change_done'): HTTPStatus.FOUND.value,
            reverse('users:password_reset_form'): HTTPStatus.OK.value,
            reverse('users:password_reset_done'): HTTPStatus.OK.value,
            reverse(
                'users:password_reset_confirm',
                kwargs={'uidb64': 'uidb64', 'token': 'token'}
            ): HTTPStatus.OK.value,
            reverse('users:password_reset_complete'): HTTPStatus.OK.value,
        }
        for reverse_name, code in pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, code)

    def test_users_pages_accessible_by_name_auth(self):
        """Страницы доступны авторизированному пользователю."""
        pages_names = {
            reverse('users:password_change_form'): HTTPStatus.OK.value,
            reverse('users:password_change_done'): HTTPStatus.OK.value,
        }
        for reverse_name, code in pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, code)

    def test_users_pages_use_correct_template(self):
        """При запросе применяется правильный шаблон."""
        templates = {
            'users:signup': 'users/signup.html',
            'users:login': 'users/login.html',
            'users:logout': 'users/logged_out.html',
        }
        for name, template in templates.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse(name))
                self.assertTemplateUsed(response, template)

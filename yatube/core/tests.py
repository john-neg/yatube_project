from http import HTTPStatus

from django.test import TestCase, Client


class ViewTestClass(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_error_page(self):
        """Проверка обработки ошибки 404"""
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)
        self.assertTemplateUsed(response, 'core/404.html')

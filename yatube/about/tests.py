from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_url_page_in_its_location(self):
        """Тест URL страниц приложения About."""
        pages_url_names = {
            '/about/author/': HTTPStatus.OK.value,
            '/about/tech/': HTTPStatus.OK.value,
        }
        for address, code in pages_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)


class AboutViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_accessible_by_name(self):
        """Тест names страниц приложения About."""
        pages_names = {
            'about:author': HTTPStatus.OK.value,
            'about:tech': HTTPStatus.OK.value,
        }
        for name, code in pages_names.items():
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertEqual(response.status_code, code)

    def test_pages_use_correct_template(self):
        """При запросе применяется правильный шаблон."""
        templates = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }
        for name, template in templates.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse(name))
                self.assertTemplateUsed(response, template)

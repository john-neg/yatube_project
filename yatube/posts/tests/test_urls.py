from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='AuthorUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст тестового сообщения',
            group=cls.group,
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаем клиент автора
        self.author_client = Client()
        self.author_client.force_login(PostURLTests.user)

    def test_urls_exists_at_desired_location(self):
        """
        HTTPStatus.OK (200) - Страницы доступны любому пользователю.
        HTTPStatus.FOUND (302) - Страницы, где нужна авторизация - недоступны
        HTTPStatus.NOT_FOUND (404) - Несуществующая страница возвращает ошибку
        """
        pages_url_names = {
            '/': HTTPStatus.OK.value,
            f'/group/{PostURLTests.group.slug}/': HTTPStatus.OK.value,
            f'/profile/{PostURLTests.user.username}/': HTTPStatus.OK.value,
            f'/posts/{PostURLTests.post.id}/': HTTPStatus.OK.value,
            '/create/': HTTPStatus.FOUND.value,
            f'/posts/{PostURLTests.post.id}/edit/': HTTPStatus.FOUND.value,
            '/non-exist-page/': HTTPStatus.NOT_FOUND.value,
        }
        for address, code in pages_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_urls_available_for_authorized(self):
        """
        HTTPStatus.OK (200) - Страницы доступны авторизированному пользователю.
        HTTPStatus.FOUND (302) - Страницы доступны только для автора
        """
        pages_url_names = {
            f'/posts/{PostURLTests.post.id}/edit/': HTTPStatus.FOUND.value,
            '/create/': HTTPStatus.OK.value,
        }
        for address, code in pages_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_edit_urls_available_only_for_author(self):
        """
        Страницы редактирования доступны только автору
        Правильный редирект для не авторов
        """
        response = self.author_client.get(
            f'/posts/{PostURLTests.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

        response = self.guest_client.get(
            f'/posts/{PostURLTests.post.id}/edit/'
        )
        self.assertRedirects(
            response,
            f"{reverse('users:login')}"
            + f"?next=/posts/{PostURLTests.post.id}/edit/"
        )
        response = self.authorized_client.get(
            f'/posts/{PostURLTests.post.id}/edit/'
        )
        self.assertRedirects(
            response, f"/posts/{PostURLTests.post.id}/"
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostURLTests.user.username}/': 'posts/profile.html',
            f'/posts/{PostURLTests.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{PostURLTests.post.id}/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)

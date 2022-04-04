import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='AuthorUser')
        cls.group = Group.objects.create(
            title='Новая тестовая группа',
            slug='test-slug',
            description='Тестовое описание новой группы',
        )
        cls.group2 = Group.objects.create(
            title='2 тестовая группа',
            slug='test-slug-2',
            description='Тестовое описание 2 группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст нового тестового сообщения',
            group=cls.group,
        )
        cls.post2 = Post.objects.create(
            author=cls.user,
            text='Тестовый текст 2 тестового сообщения',
            group=cls.group2,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаем клиент автора
        self.author_client = Client()
        self.author_client.force_login(PostFormsTests.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        # Подготавливаем данные для передачи в форму
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст другого тестового сообщения',
            'group': PostFormsTests.group.id,
            'image': uploaded,
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': PostFormsTests.user.username}
        ))
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1,
            "Количество постов не изменилось"
        )
        self.assertTrue(
            Post.objects.filter(
                author=PostFormsTests.user,
                text='Тестовый текст другого тестового сообщения',
                group=PostFormsTests.group,
                image='posts/small.gif'
            ).exists(),
            "Сообщение не создано")

    def test_create_post_unauthorised(self):
        """Проверка создания поста не авторизированным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тест создания сообщения гостем',
            'group': PostFormsTests.group.pk,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next={reverse('posts:post_create')}"
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count,
            "Количество постов изменилось"
        )

    def test_create_post_no_group(self):
        """Создание записи в Post без указания группы."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст сообщения без группы',
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': PostFormsTests.user.username}
        ))
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1,
            "Количество постов не изменилось"
        )
        self.assertTrue(
            Post.objects.filter(
                author=PostFormsTests.user,
                text='Тестовый текст сообщения без группы',
                group=None
            ).exists(),
            "Сообщение не создано")

    def test_edit_post(self):
        """Валидная форма изменяет пост с post_id."""
        post_id = PostFormsTests.post.pk
        pub_date = PostFormsTests.post.pub_date
        posts_count = Post.objects.count()
        form_edit_data = {
            'text': 'Измененное тестовое сообщение',
            'group': PostFormsTests.group2.pk,
        }
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=form_edit_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post_id}
        ))
        self.assertEqual(
            Post.objects.count(),
            posts_count,
            "Изменилось количество постов"
        )
        self.assertTrue(
            Post.objects.filter(
                author=PostFormsTests.user,
                text='Измененное тестовое сообщение',
                group=PostFormsTests.group2,
                pub_date=pub_date
            ).exists(),
            "Сообщение не изменилось")

    def test_edit_post_without_group(self):
        post_id = PostFormsTests.post2.pk
        pub_date = PostFormsTests.post2.pub_date
        form_edit_no_group = {
            'text': 'Измененное тестовое сообщение без группы'
        }
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=form_edit_no_group,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post_id}
        ))
        self.assertFalse(
            Post.objects.filter(
                author=PostFormsTests.user,
                text='Измененное тестовое сообщение без группы',
                group=PostFormsTests.group2,
                pub_date=pub_date
            ).exists(),
            "Сообщение отредактировано без группы")

    def test_edit_post_by_guest(self):
        """Проверка изменения поста не авторизированным пользователем."""
        post_id = PostFormsTests.post.pk
        posts_count = Post.objects.count()
        pub_date = PostFormsTests.post.pub_date
        form_guest_edit = {
            'text': 'Сообщение изменено гостем',
            'group': PostFormsTests.group2.pk,
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=form_guest_edit,
            follow=True
        )
        self.assertRedirects(
            response,
            (f"{reverse('users:login')}?next="
             + f"{reverse('posts:post_edit', kwargs={'post_id': post_id})}")
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count,
            "Изменилось количество постов"
        )
        self.assertFalse(
            Post.objects.filter(
                author=PostFormsTests.user,
                text='Сообщение изменено гостем',
                group=PostFormsTests.group2,
                pub_date=pub_date
            ).exists(),
            "Сообщение изменено гостем")

    def test_edit_post_by_non_author(self):
        """Проверка изменения поста не автором."""
        post_id = PostFormsTests.post.pk
        posts_count = Post.objects.count()
        pub_date = PostFormsTests.post.pub_date
        form_non_author_edit = {
            'text': 'Сообщение изменено не автором',
            'group': PostFormsTests.group2.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=form_non_author_edit,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post_id}
        ))
        self.assertEqual(
            Post.objects.count(),
            posts_count,
            "Изменилось количество постов"
        )
        self.assertFalse(
            Post.objects.filter(
                author=PostFormsTests.user,
                text='Сообщение изменено не автором',
                group=PostFormsTests.group2,
                pub_date=pub_date
            ).exists(),
            "Сообщение изменено не автором")

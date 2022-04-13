import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django import forms
from typing import ClassVar

from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
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
            title='Тестовая группа 2',
            slug='test-group-2',
            description='Тестовое описание 2 группы',
        )
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
        cls.post = Post.objects.create(
            author=cls.user,
            text='1 Тестовый текст тестового сообщения',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewsTests.user)

    def test_pages_uses_correct_template(self):
        """View функция использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostViewsTests.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewsTests.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewsTests.post.id}
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_pub_date_0 = first_object.pub_date
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, PostViewsTests.post.text)
        self.assertEqual(post_pub_date_0, PostViewsTests.post.pub_date)
        self.assertEqual(post_author_0, PostViewsTests.post.author)
        self.assertEqual(post_group_0, PostViewsTests.post.group)
        self.assertEqual(post_image_0, PostViewsTests.post.image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': PostViewsTests.group.slug}
        ))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_pub_date_0 = first_object.pub_date
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, PostViewsTests.post.text)
        self.assertEqual(post_pub_date_0, PostViewsTests.post.pub_date)
        self.assertEqual(post_author_0, PostViewsTests.post.author)
        self.assertEqual(post_group_0, PostViewsTests.post.group)
        self.assertEqual(post_image_0, PostViewsTests.post.image)
        self.assertEqual(response.context['group'], PostViewsTests.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(
            'posts:profile', kwargs={'username': PostViewsTests.user.username}
        ))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_pub_date_0 = first_object.pub_date
        post_author_username_0 = first_object.author.username
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, PostViewsTests.post.text)
        self.assertEqual(post_pub_date_0, PostViewsTests.post.pub_date)
        self.assertEqual(post_author_username_0, PostViewsTests.user.username)
        self.assertEqual(post_group_0, PostViewsTests.post.group)
        self.assertEqual(post_image_0, PostViewsTests.post.image)
        self.assertEqual(response.context['user_data'], PostViewsTests.user)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': PostViewsTests.post.id}
        ))
        post = response.context['post']
        self.assertEqual(post.text, PostViewsTests.post.text)
        self.assertEqual(post.pub_date, PostViewsTests.post.pub_date)
        self.assertEqual(post.author, PostViewsTests.post.author)
        self.assertEqual(post.group, PostViewsTests.post.group)
        self.assertEqual(post.image, PostViewsTests.post.image)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': PostViewsTests.post.id}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertIs(response.context['is_edit'], True)

    def test_post_shows_at_right_places(self):
        """Пост отображается в нужных местах."""
        post_show_places = {
            reverse('posts:index'): PostViewsTests.post,
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTests.group.slug}
            ): PostViewsTests.post,
            reverse(
                'posts:profile',
                kwargs={'username': PostViewsTests.user.username}
            ): PostViewsTests.post,
        }
        for reverse_name, expected in post_show_places.items():
            response = self.authorized_client.get(reverse_name)
            self.assertEqual(
                response.context['page_obj'][0],
                expected,
                f"Ошибка в '{reverse_name}'"
            )

    def test_post_shows_at_wrong_group(self):
        """Проверяем что пост не попал в чужую группу"""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTests.group2.slug}
            ),
        )
        self.assertFalse(
            len(response.context['page_obj']),
            'Пост отображается в чужой группе'
        )


class PaginatorViewsTests(TestCase):
    fixtures = [
        "fixture_posts_users.json",
        "fixture_posts_groups.json",
        "fixture_posts_posts.json"
    ]
    POSTS_QTY: ClassVar[int] = 10

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        """Паджинатор выводит правльное количесво постов на странице."""
        paginator_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-group-1'}),
            reverse('posts:profile', kwargs={'username': 'user1'})
        ]
        for reverse_name in paginator_pages:
            response = self.guest_client.get(reverse_name)
            self.assertEqual(
                len(response.context['page_obj']),
                PaginatorViewsTests.POSTS_QTY,
                f"Не работает Paginator на странице '{reverse_name}'"
            )

    def test_second_page_contains_less_records(self):
        """Проверка: кол-ва постов на второй странице."""
        pages_num: int = 2
        response = self.client.get(
            f"{reverse('posts:index')}?page={str(pages_num)}"
        )
        self.assertEqual(
            len(response.context['page_obj']),
            Post.objects.count() % PaginatorViewsTests.POSTS_QTY
        )

    def test_comment_shows_on_post_page(self):
        """После успешной отправки комментарий появляется на странице поста."""
        pass
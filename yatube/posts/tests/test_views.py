import shutil
import tempfile
from typing import ClassVar

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..models import Group, Post, Comment, User, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    """Тесты для проверки Views приложения Posts."""

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
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый комментарий',
            post=cls.post,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewsTests.user)

    def test_pages_uses_correct_template(self):
        """View функция использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsViewsTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostsViewsTests.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsViewsTests.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsViewsTests.post.id}
            ): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
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
        self.assertEqual(post_text_0, PostsViewsTests.post.text)
        self.assertEqual(post_pub_date_0, PostsViewsTests.post.pub_date)
        self.assertEqual(post_author_0, PostsViewsTests.post.author)
        self.assertEqual(post_group_0, PostsViewsTests.post.group)
        self.assertEqual(post_image_0, PostsViewsTests.post.image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': PostsViewsTests.group.slug}
        ))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_pub_date_0 = first_object.pub_date
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, PostsViewsTests.post.text)
        self.assertEqual(post_pub_date_0, PostsViewsTests.post.pub_date)
        self.assertEqual(post_author_0, PostsViewsTests.post.author)
        self.assertEqual(post_group_0, PostsViewsTests.post.group)
        self.assertEqual(post_image_0, PostsViewsTests.post.image)
        self.assertEqual(response.context['group'], PostsViewsTests.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(
            'posts:profile', kwargs={'username': PostsViewsTests.user.username}
        ))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_pub_date_0 = first_object.pub_date
        post_author_username_0 = first_object.author.username
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, PostsViewsTests.post.text)
        self.assertEqual(post_pub_date_0, PostsViewsTests.post.pub_date)
        self.assertEqual(post_author_username_0, PostsViewsTests.user.username)
        self.assertEqual(post_group_0, PostsViewsTests.post.group)
        self.assertEqual(post_image_0, PostsViewsTests.post.image)
        self.assertEqual(response.context['author'], PostsViewsTests.user)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': PostsViewsTests.post.id}
        ))
        post = response.context['post']
        self.assertEqual(post.text, PostsViewsTests.post.text)
        self.assertEqual(post.pub_date, PostsViewsTests.post.pub_date)
        self.assertEqual(post.author, PostsViewsTests.post.author)
        self.assertEqual(post.group, PostsViewsTests.post.group)
        self.assertEqual(post.image, PostsViewsTests.post.image)

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
            kwargs={'post_id': PostsViewsTests.post.id}
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
            reverse('posts:index'): PostsViewsTests.post,
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsViewsTests.group.slug}
            ): PostsViewsTests.post,
            reverse(
                'posts:profile',
                kwargs={'username': PostsViewsTests.user.username}
            ): PostsViewsTests.post,
        }
        for reverse_name, expected in post_show_places.items():
            response = self.authorized_client.get(reverse_name)
            self.assertEqual(
                response.context['page_obj'][0],
                expected,
                f"Ошибка в '{reverse_name}'"
            )

    def test_post_shows_at_wrong_group(self):
        """Проверяем что пост не попал в чужую группу."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsViewsTests.group2.slug}
            ),
        )
        self.assertFalse(
            len(response.context['page_obj']),
            'Пост отображается в чужой группе'
        )

    def test_comment_form_shows_on_post_detail_page(self):
        """
        Проверка, что на странице post_detail
        существует форма для оставления комментария.
        """
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsViewsTests.post.id}
            ),
        )
        self.assertTrue(
            response.context['form'],
            "Форма не существует"
        )

    def test_comment_shows_on_post_page(self):
        """После успешной отправки комментарий появляется на странице поста."""
        response = self.guest_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': PostsViewsTests.post.id}
        ))
        post = response.context['post']
        self.assertEqual(post.comments, PostsViewsTests.post.comments)


class CacheViewsTests(TestCase):
    """Тесты для проверки работы кеша."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='AuthorUser')
        cls.group = Group.objects.create(
            title='Новая тестовая группа',
            slug='test-slug',
            description='Тестовое описание новой группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='1 Тестовый текст тестового сообщения',
            group=cls.group,
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

    def test_cache_work_on_index_page(self):
        """Кэш работает на странице index."""
        response = self.guest_client.get(reverse('posts:index'))
        cache_data = response.content
        self.post.delete()
        response2 = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(cache_data, response2.content)
        cache.clear()
        response3 = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(cache_data, response3.content)


class PaginatorViewsTests(TestCase):
    """Тесты для проверки паджинатора."""

    fixtures = [
        "fixture_posts_users.json",
        "fixture_posts_groups.json",
        "fixture_posts_posts.json"
    ]
    POSTS_QTY: ClassVar[int] = 10

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        """Паджинатор выводит правильное количество постов на странице."""
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


class FollowerViewsTest(TestCase):
    """Тесты для проверки подписчиков."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.user2 = User.objects.create_user(username='user2')
        cls.author = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            author=cls.author,
            text='1 Тестовый текст тестового сообщения',
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(FollowerViewsTest.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(FollowerViewsTest.user2)

    def test_user_follow(self):
        """Проверка, что пользователь может подписываться."""
        user = self.user2
        first_count = self.author.following.filter(user=user).count()
        self.authorized_client2.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.author.username}
        ))
        second_count = self.author.following.filter(user=user).count()
        self.assertEqual(
            second_count,
            first_count + 1,
            'Не работает подписка'
        )

    def test_user_unfollow(self):
        """Проверка, что пользователь может отписываться."""
        first_count = self.author.following.filter(user=self.user).count()
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.author.username}
        ))
        second_count = self.author.following.filter(user=self.user).count()
        self.assertEqual(
            second_count,
            first_count - 1,
            'Не работает отписка'
        )

    def test_follow_index_shows_right_posts(self):
        """
        Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан.
        """
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.author.username}
        ))
        post = Post.objects.create(
            author=self.author,
            text='2 Тестовый текст тестового сообщения',
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            post,
            response.context['page_obj'][0],
            'Не отображается пост автора по подписке'
        )
        response2 = self.authorized_client2.get(reverse('posts:follow_index'))
        self.assertFalse(
            post in response2.context['page_obj'],
            'Отображается пост автора на которого не подписан'
        )

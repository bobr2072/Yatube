import shutil
import tempfile

from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User
from yatube.settings import page_objects

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostPagesTests(TestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='test_user_views')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.author = User.objects.create_user(
            username='test_author_views'
        )
        cls.auth_author_client = Client()
        cls.auth_author_client.force_login(cls.author)
        cls.not_author = User.objects.create_user(
            username='test_not_author_views'
        )
        cls.auth_not_author_client = Client()
        cls.auth_not_author_client.force_login(cls.not_author)
        cls.user_follower = User.objects.create_user(
            username='follower'
        )
        cls.authorized_client_follower = Client()
        cls.authorized_client_follower.force_login(cls.user_follower)

        cls.small_jpg = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )

        cls.uploaded = SimpleUploadedFile(
            name='test.jpg',
            content=cls.small_jpg,
            content_type='image/jpg'
        )

        cls.group = Group.objects.create(
            title='test_group_views',
            slug='test-slug_views',
            description='test_description_views'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст вьюх',
            author=cls.author,
            group=cls.group,
            image=cls.uploaded
        )

        cls.follow = Follow.objects.create(
            user=cls.not_author,
            author=cls.author
        )

    def test_pages_uses_correct_template(self):
        """views использует соответствующий шаблон."""

        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                args=[self.group.slug],
            ),
            'posts/post_create.html': reverse('posts:post_create'),
            'posts/profile.html': reverse(
                'posts:profile',
                args=[self.author.username]
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                args=[self.post.pk]
            ),
            'posts/post_edit.html': reverse(
                'posts:post_edit',
                args=[self.post.pk]
            ),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.auth_author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.auth_author_client.get(reverse('posts:index'))
        response_post = response.context.get('page_obj').object_list[0]
        views_context = {
            response_post.author: self.post.author,
            response_post.group: self.post.group,
            response_post.text: self.post.text,
            response_post.image: self.post.image
        }
        for view_response, name in views_context.items():
            with self.subTest(name=name):
                self.assertEqual(view_response, name)

    def test_group_list_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.auth_author_client.get(reverse(
            'posts:group_list',
            args=[self.group.slug]
        ))
        response_post = response.context.get('page_obj').object_list[0]
        views_context = {
            response_post.author: self.post.author,
            response_post.group: self.post.group,
            response_post.text: self.post.text,
            response_post.image: self.post.image,
        }
        for view_response, name in views_context.items():
            with self.subTest(name=name):
                self.assertEqual(view_response, name)

    def test_profile_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.auth_author_client.get(reverse(
            'posts:profile',
            args=[self.author.username]
        ))
        response_post = response.context.get('page_obj').object_list[0]
        views_context = {
            response_post.author: self.post.author,
            response_post.group: self.post.group,
            response_post.text: self.post.text,
            response_post.image: self.post.image,
        }
        for view_response, name in views_context.items():
            with self.subTest(name=name):
                self.assertEqual(view_response, name)

    def test_post_detail_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.auth_author_client.get(reverse(
            'posts:post_detail',
            args=[self.post.pk]
        ))
        response_post = response.context.get('post')
        views_context = {
            response_post.author: self.post.author,
            response_post.group: self.post.group,
            response_post.text: self.post.text,
            response_post.image: self.post.image,
            response_post: self.post,
        }
        for view_response, name in views_context.items():
            with self.subTest(name=name):
                self.assertEqual(view_response, name)

    def test_post_create_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.auth_author_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.auth_author_client.get(reverse(
            'posts:post_edit',
            args=[self.post.pk]
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_authorized_client_comment(self):
        """Авторизованный пользователь может комментировать посты."""
        form_data = {
            'text': 'Authorized test comment',
            'post': self.post,
            'author': self.author.username
        }
        form_text = form_data['text']

        self.auth_not_author_client.post(
            reverse(
                'posts:add_comment',
                args=[self.post.id]
            ),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Comment.objects.filter(
                text=form_text
            ).exists()
        )

        response = self.auth_not_author_client.get(
            reverse('posts:post_detail', args=[self.post.pk])
        )
        comment = Comment.objects.last()
        self.assertIn(comment, response.context['comments'])

    def test_authorized_client_follow(self):
        """Авторизованный пользователь может подписываться на авторов."""
        author_follow = reverse('posts:profile_follow', args=[self.user])
        count_folow = Follow.objects.count()
        response = self.authorized_client_follower.get(author_follow)
        self.assertEqual(Follow.objects.count(), count_folow + 1)
        self.assertEqual(response.status_code, 302)

    def test_authorized_client_unfollow(self):
        """Авторизованный пользователь может отписиваться от авторов."""
        author_follow = reverse('posts:profile_follow', args=[self.user])
        response = self.authorized_client_follower.get(author_follow)
        author_unfollow = reverse('posts:profile_unfollow', args=[self.user])
        count_unfolow = Follow.objects.count()
        response = self.authorized_client_follower.get(author_unfollow)
        self.assertEqual(Follow.objects.count(), count_unfolow - 1)
        self.assertEqual(response.status_code, 302)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='test_description'
        )
        objs = [
            Post(
                text=f'test_post_view{i}',
                group=cls.group,
                author=cls.author)
            for i in range(13)
        ]
        Post.objects.bulk_create(objs)

    def test_first_index_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), page_objects)

    def test_second_index_page_contains_three_records(self):
        response = self.authorized_client.get(reverse(
            'posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_group_list_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            args=[self.group.slug]
        ))
        self.assertEqual(len(response.context['page_obj']), page_objects)

    def test_second_group_list_page_contains_three_records(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            args=[self.group.slug]) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_profile_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse(
            'posts:profile',
            args=[self.author.username]
        ))
        self.assertEqual(len(response.context['page_obj']), page_objects)

    def test_second_profile_page_contains_three_records(self):
        response = self.authorized_client.get(reverse(
            'posts:profile',
            args=[self.author.username]) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

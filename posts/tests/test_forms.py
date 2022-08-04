import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostFormTests(TestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
        cls.author = User.objects.create_user(
            username='test_author_forms'
        )
        cls.auth_author_client = Client()
        cls.auth_author_client.force_login(cls.author)
        cls.not_author = User.objects.create_user(
            username='test_not_author_forms'
        )
        cls.authorized_not_author_client = Client()
        cls.authorized_not_author_client.force_login(cls.not_author)

        cls.small_jpg = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )

        cls.not_jpg = ('nothing')

        cls.uploaded = SimpleUploadedFile(
            name='test.jpg',
            content=cls.small_jpg,
            content_type='image/jpg'
        )

        cls.group = Group.objects.create(
            title='test_group_forms',
            slug='test-slug_forms',
            description='test_description_forms'
        )

        cls.post = Post.objects.create(
            text='FORM_TEST_TEXT',
            group=cls.group,
            author=cls.author,
        )

        cls.form = PostForm()

    def test_post_create(self):
        """Форма Post создает запись"""
        posts_count = Post.objects.count()
        last_post = Post.objects.all()[0]
        new_post = Post.objects.filter(
            text='Текст поста из формы',
            group=self.group,
            image='posts/test.jpg'
        )
        form_data = {
            'text': 'Текст поста из формы',
            'group': self.group.pk,
            'image': self.uploaded
        }
        response = self.auth_author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(new_post.exists())
        self.assertEqual(
            Post.objects.all().order_by('pub_date')[0],
            last_post
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            args=[self.author.username]
        ))

    def test_not_image_post_create(self):
        """При попытке загрузить не картинку пост не создаётся"""
        bad_post = Post.objects.filter(
            text='Текст поста из формы2',
            group=self.group,
            image='posts/nothing'
        )
        bad_form_data = {
            'text': 'Текст поста из формы2',
            'group': self.group.pk,
            'image': self.not_jpg
        }
        self.auth_author_client.post(
            reverse('posts:post_create'),
            data=bad_form_data,
            follow=True,
        )
        self.assertFalse(bad_post.exists())

    def test_edit_post(self):
        """Запись успешно редактируется"""

        form_data = {
            'text': 'Текст поста из формы',
            'group': self.group.pk
        }
        self.auth_author_client.post(
            reverse(
                'posts:post_edit',
                args=[self.post.pk]
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.get(pk=self.post.pk).text,
            form_data['text'])

from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import Group, Post, User


class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser_urls')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.author = User.objects.create_user(
            username='test_author_urls'
        )
        cls.auth_author_client = Client()
        cls.auth_author_client.force_login(cls.author)
        cls.not_author = User.objects.create_user(
            username='test_not_author_urls'
        )
        cls.authorized_not_author_client = Client()
        cls.authorized_not_author_client.force_login(cls.not_author)

        cls.group = Group.objects.create(
            title='test_group_urls',
            slug='test-slug_urls',
            description='test_description_urls'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст моделей',
            author=cls.user,
            group=cls.group,
        )

    def test_custom_404(self):
        """Проверка, что страница 404 отдает кастомный шаблон"""
        response = self.authorized_client.get('not_found')
        self.assertTemplateUsed(response, 'core/404.html')
        self.assertEqual(HTTPStatus.NOT_FOUND, 404)

    def test_custom_403(self):
        """Проверка, что страница 403 отдает кастомный шаблон"""
        response = self.authorized_client.get('/403')
        self.assertTemplateUsed(response, 'core/403.html')

    def test_custom_500(self):
        """Проверка, что страница 500 отдает кастомный шаблон"""
        response = self.authorized_client.get('/500')
        self.assertTemplateUsed(response, 'core/500.html')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.user}/',
            'posts/post_detail.html': f'/posts/{self.post.pk}/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_authorized_correct_template_create(self):
        """post_create использует соответствующий шаблон"""
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/post_create.html')

    def test_urls_author_correct_template_post_edit(self):
        """post_edit использует соответствующий шаблон"""
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertTemplateUsed(response, 'posts/post_edit.html')

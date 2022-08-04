from django.test import TestCase

from posts.models import Comment, Follow, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user_models')
        cls.followed_author = User.objects.create_user(
            username='test_author_models'
        )

        cls.group = Group.objects.create(
            title='Тестовая группа моделей',
            slug='Тестовый слаг моделей',
            description='Тестовое описание моделей',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост моделей',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий моделей'
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.followed_author
        )

    def test_post_model_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        verbose = self.post._meta.get_field('text').verbose_name
        self.assertEqual(verbose, 'Текст поста')

    def test_group_model_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        verbose = self.group._meta.get_field('title').verbose_name
        self.assertEqual(verbose, 'Название группы')

    def test_comment_model_have_correct_object_names(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        verbose = self.comment._meta.get_field('text').verbose_name
        self.assertEqual(verbose, 'Текст комментария')

    def test_comment_model_have_correct_object_names(self):
        """Проверяем, что у модели Follow корректно отображаются поля."""
        verbose1 = self.follow._meta.get_field('user').verbose_name
        verbose2 = self.follow._meta.get_field('author').verbose_name
        self.assertEqual(verbose1, 'Подписывающийся юзер')
        self.assertEqual(verbose2, 'Автор, на которого подписываются')

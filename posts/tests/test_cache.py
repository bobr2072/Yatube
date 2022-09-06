from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from yatube.settings import CACHES as cache


class CacheTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='cache_test_user')
        cls.group = Group.objects.create(title='test_cache_group',
                                         slug='cache_test',
                                         description='cache_group')
        cls.guest_client = Client()

    def test_cache_index(self):
        response = self.guest_client.get(reverse('posts:index'))
        post_not_in_cache = Post.objects.create(text='test_post_cache',
                                                author=self.user,
                                                group=self.group)
        self.assertTrue(Post.objects.filter(id=post_not_in_cache.id).exists())
        self.assertEqual(len(response.context['page_obj'].object_list),
                         Post.objects.count() - 1)
        cache.clear()
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj'].object_list),
                         Post.objects.count())

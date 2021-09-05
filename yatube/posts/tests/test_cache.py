from django.urls import reverse
from django.test import TestCase, Client

from ..models import Post, User


class CachesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='текст поста',
        )

    def setUp(self):
        self.client = Client()

    def test_cache(self):
        content_post = self.client.get(
            reverse('posts:home_page')).content
        self.post.delete()
        content_delete_post = self.client.get(
            reverse('posts:home_page')).content
        self.assertEqual(content_post, content_delete_post)

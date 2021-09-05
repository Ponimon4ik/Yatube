from django.test import TestCase
from django.urls import reverse

from ..models import Post, Group, User

USERNAME = 'auth1'
SLUG = 'test-slug'


class RoutesTests(TestCase):

    def testing_route_name(self):
        """Тест имен маршрутов"""
        post = Post.objects.create(
            author=User.objects.create_user(username=USERNAME),
            text='Тестовый текст',
            group=Group.objects.create(slug=SLUG)
        )
        route_name_lists = [
            ['/', 'posts:home_page', []],
            [f'/profile/{post.author.username}/',
             'posts:profile', [post.author.username]],
            [f'/posts/{post.id}/', 'posts:post_detail', [post.id]],
            ['/create/', 'posts:post_create', []],
            [f'/group/{post.group.slug}/',
             'posts:group_list', [post.group.slug]],
            [f'/posts/{post.id}/edit/', 'posts:post_edit', [post.id]],
            ['/follow/', 'posts:follow_index', []],
            [f'/posts/{post.id}/comment', 'posts:add_comment', [post.id]],
            [f'/profile/{post.author.username}/follow/',
             'posts:profile_follow', [post.author.username]],
            [f'/profile/{post.author.username}/unfollow/',
             'posts:profile_unfollow', [post.author.username]],
        ]
        for explicit_url, reverse_name, argument in route_name_lists:
            with self.subTest(explicit_url=explicit_url):
                url = reverse(reverse_name, args=argument)
                self.assertEqual(explicit_url, url)

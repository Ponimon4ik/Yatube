from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User

USERNAMES = ['auth1', 'reader']
SLUG = 'test-slug'
HOME_PAGE_URL = reverse('posts:home_page')
SELECTED_POSTS_URL = reverse('posts:follow_index')
CREATE_POST_URL = reverse('posts:post_create')
GROUP_URL = reverse('posts:group_list',
                    args=[SLUG])
USER1_URL = reverse('posts:profile',
                    args=[USERNAMES[0]])
FOLLOW_AUTHOR_URL = reverse('posts:profile_follow',
                            args=[USERNAMES[0]])
UNFOLLOW_AUTHOR_URL = reverse('posts:profile_follow',
                              args=[USERNAMES[0]])
AUTHORIZATION_URL = reverse('users:login')


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_lists = [User.objects.create_user(username=username)
                          for username in USERNAMES]
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_lists[0],
            text='Тестовый текст',
            group=cls.group
        )
        cls.POST_URL = reverse(
            'posts:post_detail',
            args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit',
                                    args=[cls.post.id])
        cls.ADD_COMMENT_URL = reverse('posts:add_comment',
                                      args=[cls.post.id])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client1 = Client()
        self.authorized_client2 = Client()
        self.authorized_client1.force_login(self.user_lists[0])
        self.authorized_client2.force_login(self.user_lists[1])

    # Проверка доступности страниц
    def test_public_pages_url(self):
        """Доступность страниц"""
        # Адрес - клиент - код ответа
        cases = [
            [HOME_PAGE_URL, self.guest_client, 200],
            [SELECTED_POSTS_URL, self.authorized_client2, 200],
            [GROUP_URL, self.guest_client, 200],
            [USER1_URL, self.guest_client, 200],
            [self.POST_URL, self.guest_client, 200],
            [self.POST_EDIT_URL, self.authorized_client1, 200],
            [CREATE_POST_URL, self.authorized_client1, 200],
            [self.POST_EDIT_URL, self.guest_client, 302],
            [CREATE_POST_URL, self.guest_client, 302],
            [CREATE_POST_URL, self.guest_client, 302],
            [self.POST_EDIT_URL, self.authorized_client2, 302],
            [self.ADD_COMMENT_URL, self.authorized_client2, 302],
            [self.ADD_COMMENT_URL, self.guest_client, 302],
            [SELECTED_POSTS_URL, self.guest_client, 302],
            [FOLLOW_AUTHOR_URL, self.guest_client, 302],
            [FOLLOW_AUTHOR_URL, self.authorized_client2, 302],
            [UNFOLLOW_AUTHOR_URL, self.guest_client, 302],
            [UNFOLLOW_AUTHOR_URL, self.authorized_client2, 302],
            ['/unexisting_page/', self.authorized_client1, 404],
        ]
        for url, client, status_code in cases:
            with self.subTest(url=url, client=client):
                self.assertEqual(client.get(url).status_code, status_code)

    # Проверка редирект
    def test_pages_url_redirect(self):
        """Проверка redirect"""
        # Адрес - клиент - редирект адрес
        cases = [
            [CREATE_POST_URL,
             self.guest_client,
             AUTHORIZATION_URL + '?next=' + CREATE_POST_URL],
            [self.POST_EDIT_URL,
             self.guest_client,
             AUTHORIZATION_URL + '?next=' + self.POST_EDIT_URL],
            [self.POST_EDIT_URL,
             self.authorized_client2,
             self.POST_URL],
            [self.ADD_COMMENT_URL,
             self.authorized_client2,
             self.POST_URL],
            [self.ADD_COMMENT_URL,
             self.guest_client,
             AUTHORIZATION_URL + '?next=' + self.ADD_COMMENT_URL],
            [SELECTED_POSTS_URL,
             self.guest_client,
             AUTHORIZATION_URL + '?next=' + SELECTED_POSTS_URL],
            [FOLLOW_AUTHOR_URL,
             self.guest_client,
             AUTHORIZATION_URL + '?next=' + FOLLOW_AUTHOR_URL],
            [FOLLOW_AUTHOR_URL,
             self.authorized_client2,
             USER1_URL],
            [UNFOLLOW_AUTHOR_URL,
             self.guest_client,
             AUTHORIZATION_URL + '?next=' + UNFOLLOW_AUTHOR_URL],
            [UNFOLLOW_AUTHOR_URL,
             self.authorized_client2,
             USER1_URL],
        ]
        for url, client, redirect_url in cases:
            with self.subTest(url=url, client=client):
                self.assertRedirects(
                    client.get(url, follow=True), redirect_url
                )

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Адреса по шаблонам
        templates_pages_names = {
            HOME_PAGE_URL: 'posts/index.html',
            GROUP_URL: 'posts/group_list.html',
            USER1_URL: 'posts/profile.html',
            self.POST_URL: 'posts/post_detail.html',
            CREATE_POST_URL: 'posts/create_post.html',
            self.POST_EDIT_URL: 'posts/create_post.html',
            SELECTED_POSTS_URL: 'posts/follow.html',
            '/unexisting_page/': 'core/404.html',

        }
        for url, template in templates_pages_names.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.authorized_client1.get(url), template
                )

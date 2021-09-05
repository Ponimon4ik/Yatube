import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.conf import settings

from ..models import Post, Group, User, Comment, Follow
from ..settings import POST_COUNT

USERNAMES = ['auth', 'follower', 'unfollower']
SLUGS = ['test-slug1', 'test-slug2']
HOME_PAGE_URL = reverse('posts:home_page')
SELECTED_POSTS_URL = reverse('posts:follow_index')
GROUP1_URL = reverse('posts:group_list', args=[SLUGS[0]])
GROUP2_URL = reverse('posts:group_list', args=[SLUGS[1]])
USER1_URL = reverse('posts:profile', args=[USERNAMES[0]])
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_lists = [User.objects.create_user(username=username)
                          for username in USERNAMES]
        cls.group_lists = [
            Group.objects.create(
                title=f'группа {group_slug}',
                slug=group_slug,
                description=f'Тестовое описание{group_slug}'
            ) for group_slug in SLUGS
        ]
        cls.posts_list = []
        for i in range(1, POST_COUNT + 3):
            cls.posts_list.append(
                Post.objects.create(
                    author=cls.user_lists[0],
                    text=f'текст поста {i}',
                    group=cls.group_lists[0]
                )
            )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.post_second_group = Post.objects.create(
            author=cls.user_lists[0],
            text='текст поста второй группы',
            group=cls.group_lists[1],
            image=cls.uploaded
        )
        cls.comment_post_second_group = Comment.objects.create(
            post=cls.post_second_group,
            author=cls.user_lists[1],
            text='Тестовый комментарий'
        )
        cls.OBJ_COUNT = Post.objects.count()
        cls.POST_SECOND_GROUP_URL = reverse(
            'posts:post_detail',
            args=[cls.post_second_group.id])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.client = Client()
        self.follower = Client()
        self.unfollower = Client()
        self.follower.force_login(self.user_lists[1])
        self.unfollower.force_login(self.user_lists[2])
        Follow.objects.create(user=self.user_lists[1],
                              author=self.user_lists[0])

    # Проверяем Paginator
    def test_first_page_contains_records(self):
        """Количество постов на первой странице"""
        number_of_posts = {
            HOME_PAGE_URL: POST_COUNT,
            GROUP1_URL: POST_COUNT,
            USER1_URL: POST_COUNT,
        }
        for url, quantity in number_of_posts.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(len(response.context['page_obj']), quantity)

    def test_second_page_contains_records(self):
        """Количество постов на второй странице"""
        difference = self.OBJ_COUNT - POST_COUNT
        number_of_posts = {
            HOME_PAGE_URL: difference,
            GROUP1_URL: difference - 1,
            USER1_URL: difference,
        }
        for url, quantity in number_of_posts.items():
            with self.subTest(url=url):
                response = self.client.get(url + '?page=2')
                self.assertEqual(len(response.context['page_obj']), quantity)

    # Проверка контекста
    def test_page_context(self):
        """Проверка контекста страниц"""
        pages_context = {
            HOME_PAGE_URL: 'page_obj',
            GROUP2_URL: 'page_obj',
            USER1_URL: 'page_obj',
            SELECTED_POSTS_URL: 'page_obj',
            self.POST_SECOND_GROUP_URL: 'post',
        }
        for url, context in pages_context.items():
            with self.subTest(url=url):
                response = self.follower.get(url)
                context_page = response.context[context]
                if context == 'post':
                    post_context = context_page
                else:
                    posts_lists = [
                        post for post in context_page
                        if post.id == self.post_second_group.id]
                    self.assertEqual(len(posts_lists), 1)
                    post_context = posts_lists[0]
                self.assertEqual(
                    post_context.id,
                    self.post_second_group.id
                )
                self.assertEqual(
                    post_context.author,
                    self.post_second_group.author
                )
                self.assertEqual(
                    post_context.text,
                    self.post_second_group.text
                )
                self.assertEqual(
                    post_context.group,
                    self.post_second_group.group
                )
                self.assertEqual(
                    post_context.image,
                    self.post_second_group.image
                )

    def test_post_in_the_correct_group(self):
        """Проверка что пост с тестовой группой 2
        не попал в список постов тестовой группы 1
        """
        response = self.client.get(GROUP1_URL)
        self.assertNotIn(self.post_second_group, response.context['page_obj'])

    def test_profile_page_contains_correct_user(self):
        """Проверка страница автора
        содержит правильного пользователя"""
        response = self.client.get(USER1_URL)
        self.assertEqual(
            response.context['author'],
            self.user_lists[0]
        )

    def test_group_page_contains_correct_group(self):
        """Проверка страница группы
        содержит правильную группу"""
        response = self.client.get(GROUP2_URL)
        self.assertEqual(
            response.context['group'].title,
            self.group_lists[1].title
        )
        self.assertEqual(
            response.context['group'].slug,
            self.group_lists[1].slug
        )
        self.assertEqual(
            response.context['group'].description,
            self.group_lists[1].description
        )

    def test_comment_context_test(self):
        """Проверка контеста комментария"""
        response = self.client.get(self.POST_SECOND_GROUP_URL)
        comment_context = response.context['comments']
        self.assertEqual(len(comment_context), 1)
        comment = comment_context[0]
        self.assertEqual(comment.post, self.comment_post_second_group.post)
        self.assertEqual(
            comment.author,
            self.user_lists[1])
        self.assertEqual(comment.text, self.comment_post_second_group.text)

    def test_comment_in_the_correct_post(self):
        """Проверка что комментарий к посту с тестовой группой 2
        не попал в другой пост
        """
        response = self.client.get(self.POST_SECOND_GROUP_URL)
        comment_context = response.context['comments']
        self.assertEqual(len(comment_context), 1)
        comment = comment_context[0]
        self.assertNotIn(comment, self.posts_list[0].comments.all())

    def test_user_posts_not_subscribed_to_the_author(self):
        response = self.unfollower.get(SELECTED_POSTS_URL)
        context_page = response.context['page_obj']
        posts_lists = [post for post in context_page]
        self.assertNotIn(self.post_second_group, posts_lists)

import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, Group, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
USERNAME = 'auth'
SLUGS = ['test-slug1', 'test-slug2']
CREATE_POST_URL = reverse('posts:post_create')
USER_URL = reverse('posts:profile',
                   args=[USERNAME])


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group_lists = [Group.objects.create(slug=group_slug)
                           for group_slug in SLUGS]
        cls.first_post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group_lists[0]
        )
        cls.form = PostForm()
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit',
            args=[cls.first_post.id])
        cls.FIRST_POST_URL = reverse(
            'posts:post_detail',
            args=[cls.first_post.id])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        tasks_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст 2',
            'group': self.group_lists[0].pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            CREATE_POST_URL,
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, USER_URL)
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        # Проверяем, что создалась запись с заданным контентом
        posts = Post.objects.exclude(id=self.first_post.id)
        self.assertEqual(len(posts), 1)
        post = posts[0]
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])
        self.assertTrue(Post.objects.filter(
            image=f'posts/{form_data["image"].name}').exists())

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post."""
        # Подсчитаем количество записей в Post
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Отредактированный тестовый текст',
            'group': self.group_lists[1].pk,
        }
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, self.FIRST_POST_URL)
        # Проверяем, что число постов не увеличилось
        self.assertEqual(Post.objects.count(), tasks_count)
        # Проверяем, что контент изменился
        edited_post = response.context['post']
        self.assertEqual(edited_post.author, self.first_post.author)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group.pk, form_data['group'])

    def test_pages_correct_context(self):
        """Шаблон сформирован с правильным контекстом."""
        urls = [
            self.POST_EDIT_URL,
            CREATE_POST_URL,
        ]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            for url in urls:
                with self.subTest(value=value, url=url):
                    response = self.authorized_client.get(url)
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_create_comment(self):
        """Валидная форма создает комментарий"""
        commentator = User.objects.create_user(username='commentator')
        authorized_commentator = Client()
        authorized_commentator.force_login(commentator)
        comment_first_post_url = reverse(
            'posts:add_comment',
            args=[self.first_post.id])
        form_data = {
            'post': self.first_post,
            'author': commentator,
            'text': 'Тестовый комментарий'
        }
        response = authorized_commentator.post(
            comment_first_post_url,
            data=form_data,
            follow=True,
        )
        # Проверяем что сработал редирект
        self.assertRedirects(response, self.FIRST_POST_URL)
        # Проверяем, что создан один комментарий
        self.assertEqual(Comment.objects.count(), 1)
        # Проверяем что коментарий с заданным контентом
        comment = Comment.objects.get(post=self.first_post)
        self.assertEqual(comment.author, commentator)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.post, form_data['post'])

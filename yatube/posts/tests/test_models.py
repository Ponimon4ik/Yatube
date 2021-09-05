from django.test import TestCase

from ..models import Post, Group, User, Comment, Follow


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='больше пятнадцати символов',
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Комментарий'
        )

    def test_field_str_for_post(self):
        """Проверяем, что у модели Post корректно работает __str__"""
        self.assertEqual(str(self.post), (f'{self.post.author}, '
                                          f'{self.post.text[:15]}, '
                                          f'{self.post.group}, '
                                          f'{self.post.pub_date}')
                         )

    def test_field_str_for_group(self):
        """Проверяем, что у модели
        Group корректно работает __str__"""
        self.assertEqual(str(self.group), self.group.title)

    def test_field_str_for_comment(self):
        """Проверяем что у модели
        Comment корректно работает str"""
        self.assertEqual(str(self.comment), (f'{self.comment.author}, '
                                             f'{self.comment.text}, '
                                             f'{self.comment.created}')
                         )

    def test_field_str_for_subscription(self):
        """Проверяем, что у модели
        Follow корректно работает __str__
        """
        follower = User.objects.create_user(username='user')
        subscription = Follow.objects.create(
            user=follower,
            author=self.user
        )
        self.assertEqual(str(subscription), (f'{subscription.author}, '
                                             f'{subscription.user}'))

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group (models.Model):
    title = models.CharField(max_length=200,
                             verbose_name='название')
    slug = models.SlugField(max_length=10,
                            unique=True,
                            verbose_name='ключ')
    description = models.TextField(verbose_name='описание группы')

    class Meta:
        verbose_name = 'группа'
        verbose_name_plural = 'группы'

    def __str__(self):
        return self.title


class Post (models.Model):
    text = models.TextField(verbose_name='текст записи')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='дата публикации')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='автор')
    group = models.ForeignKey(Group,
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              related_name='posts',
                              verbose_name='группа')
    image = models.ImageField(verbose_name='Картинка',
                              upload_to='posts/',
                              blank=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'запись'
        verbose_name_plural = 'записи'

    def __str__(self):
        return (
            f'{self.author}, '
            f'{self.text[:15]}, '
            f'{self.group}, '
            f'{self.pub_date}'
        )


class Comment (models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='запись'
                             )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='автор'
                               )
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='дата коментария'
                                   )
    text = models.TextField(verbose_name='текст комментария')

    class Meta:
        ordering = ('-created',)
        verbose_name = 'комментарии'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        return (
            f'{self.author}, '
            f'{self.text[:15]}, '
            f'{self.created}'
        )


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='подписчик'
                             )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='автор'
                               )

    class Meta:
        verbose_name = 'подписки'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique subscription')
        ]

    def __str__(self):
        return (
            f'{self.author}, '
            f'{self.user}'
        )

from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel

User = get_user_model()


class Post(CreatedModel):
    text = models.TextField('Текст поста', help_text='Введите текст поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='group_page',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text


class Group(models.Model):
    title = models.CharField('Название группы', max_length=200)
    slug = models.SlugField('Адрес', unique=True)
    description = models.TextField('Описание')

    class Meta:
        verbose_name = 'Группы'

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             verbose_name='Комментируемый пост',
                             related_name='comments'
                             )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор комментария',
                               related_name='comments'
                               )
    text = models.TextField('Текст комментария')
    created = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True,
                             default=User,
                             related_name='follower',
                             verbose_name='Подписывающийся юзер',
                             )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True,
                               related_name='following',
                               verbose_name='Автор, на которого подписываются',
                               )

    class Meta:
        verbose_name = 'Подписки на авторов'
        unique_together = ['user', 'author']
        constraints = [
            models.CheckConstraint(check=~models.Q(user=models.F('author')),
                                   name='no_self_follows')
        ]

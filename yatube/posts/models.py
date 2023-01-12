from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Model for a group of posts."""

    title = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='ЧПУ',
    )
    description = models.TextField(
        verbose_name='Описание',
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self) -> str:
        return f'{self.title}'


class Post(models.Model):
    """Model for posts."""

    text = models.TextField(
        verbose_name='Текст',
        help_text='Текст поста',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.text[:15]}'


class Comment(models.Model):
    """Model of comments."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.text}'

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=200,
        help_text='Дайте короткое название заголовку'
    )
    slug = models.SlugField(
        verbose_name='Адрес для страницы группы',
        null=False,
        unique=True,
        help_text=('Укажите адрес для страницы группы. Используйте только '
                   'латиницу, цифры, дефисы и знаки подчёркивания'))
    description = models.TextField(
        verbose_name='Описание',
        help_text='Дайте короткое описание группе'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Опишите суть поста'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата выпуска',
        help_text='Дата выпуска',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts',
        help_text='Имя автора'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        help_text='Название группы',
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        verbose_name='Картинка',
        help_text='Картинка',
    )

    class Meta:
        ordering = ['pub_date', ]

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        help_text='Напишите комментарий',
        verbose_name='Комментарий',
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        help_text='Напишите комментарий',
        verbose_name='Комментарий '
    )
    created = models.DateTimeField(
        auto_now_add=True,
        help_text='Дата публикации комментария',
        verbose_name='Дата публикации комментария'
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User, related_name='follower', on_delete=models.CASCADE)
    author = models.ForeignKey(
        User, related_name='following', on_delete=models.CASCADE)

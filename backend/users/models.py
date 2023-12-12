from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError

import users.constants as const


class User(AbstractUser):
    """Модель пользователей."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')
    username = models.CharField(
        max_length=const.MAX_LENGTH_USER_USERNAME,
        unique=True,
        blank=False,
        verbose_name='Имя пользователя',
    )
    email = models.EmailField(
        max_length=const.MAX_LENGTH_USER_EMAIL,
        unique=True,
        blank=False,
        verbose_name='Электронная почта',
    )
    first_name = models.CharField(
        max_length=const.MAX_LENGTH_USER_NAME,
        blank=True,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=const.MAX_LENGTH_USER_NAME,
        blank=True,
        verbose_name='Фамилия',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        models.UniqueConstraint(
            fields=('user', 'author'),
            name='unique_follow'
        )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Невозможно подписаться на себя.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

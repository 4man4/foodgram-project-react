from django.db import models
from django.contrib.auth.models import AbstractUser
# from django.contrib.auth import get_user_model


# User = get_user_model()


# class Role(models.TextChoices):
#     USER = 'user', 'Пользователь'
#     MODERATOR = 'moderator', 'Модератор'
#     ADMIN = 'admin', 'Администратор'


class User(AbstractUser):
    """Модель пользователей."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        verbose_name='Имя пользователя',
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        verbose_name='Электронная почта',
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        max_length=150,
        blank=True
    )
    # role = models.CharField(
    #     max_length=len(max(Role.values, key=len)),
    #     choices=Role.choices,
    #     default=Role.USER,
    #     verbose_name='Роль',
    # )

    # def is_admin(self):
    #     return self.role == Role.ADMIN or self.is_staff
    #
    # def is_user(self):
    #     return self.role == Role.USER
    #
    # def is_moderator(self):
    #     return self.role == Role.MODERATOR
    #
    class Meta:
        # ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['username', 'email'], name='unique_username_email'
        #     )
        # ]

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        models.UniqueConstraint(
            fields=['user', 'author'],
            name='unique_follow'
        )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

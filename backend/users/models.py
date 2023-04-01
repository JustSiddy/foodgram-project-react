from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q, UniqueConstraint


class User(AbstractUser):
    """Модель пользователя."""
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.STRING_FIELD_LENGTH,
        blank=False,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.STRING_FIELD_LENGTH,
        blank=False,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=settings.STRING_FIELD_LENGTH,
    )
    email = models.EmailField(
        verbose_name='Почта',
        max_length=settings.EMAIL_FIELD_LENGTH,
        unique=True,)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscriptions',
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='no_self_follow')]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

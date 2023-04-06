from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models

from users.models import Subscription, User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('username', 'email',
                    'first_name', 'last_name')
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')
    empty_value_display = '-пусто-'
    follows = models.ManyToManyField(
        'self',
        through='Subscription',
        symmetrical=False)
    favorites_recipes = models.ManyToManyField(
        'recipes.Recipe',
        'Favorites')


@admin.register(Subscription)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ['author__username, author__email',
                     'user__username', 'user__email']
    empty_value_display = '-пусто-'

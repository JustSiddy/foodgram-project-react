from django.contrib import admin 
from django.contrib.auth.admin import UserAdmin 
 
from users.models import Subscription, User 
 
 
@admin.register(User) 
class UserAdmin(UserAdmin): 
    list_display = ('username', 'email', 
                    'first_name', 'last_name',
                    'get_recipes_count', 'get_followers_count') 
    list_filter = ('email', 'username') 
    search_fields = ('email', 'username') 
    empty_value_display = '-пусто-' 
 
    def get_recipes_count(self, obj): 
        return obj.user.count() 
    get_recipes_count.short_description = 'Рецепты' 
 
    def get_followers_count(self, obj): 
        return obj.user.count() 
    get_followers_count.short_description = 'Подписчики' 
 
 
@admin.register(Subscription) 
class SubscriptionsAdmin(admin.ModelAdmin): 
    list_display = ('id', 'user', 'author') 
    search_fields = ['author__username, author__email', 
                     'user__username', 'user__email'] 
    empty_value_display = '-пусто-' 
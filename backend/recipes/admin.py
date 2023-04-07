from django.contrib import admin
from django.contrib.auth.models import Group

from recipes.models import (Favorites, Ingredient,
                            IngredientInRecipe,
                            Recipe, ShoppingCart,
                            Tag)


class IngredientInRecipe(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'slug', 'color']
    search_fields = ['name', 'slug']
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'measurement_unit']
    search_fields = ['name']
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorites',
                    'get_tags', 'get_ingredients')
    list_filter = ['author', 'name', 'tags']
    search_fields = ['name', 'author__username']
    inlines = (IngredientInRecipe,)
    empty_value_display = '-пусто-'

    def get_tags(self, obj):
        list_ = [_.name for _ in obj.tags.all()]
        return ', '.join(list_)

    def favorites(self, obj):
        return obj.favorites.count()
    favorites.short_description = 'Избранное'

    def get_ingredients(self, obj):
        return ", ".join(
            [i for i in obj.ingredients.values_list('name', flat=True)])
    get_ingredients.short_description = 'Ингредиенты'


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'recipe']
    search_fields = ['user__username', 'user__email']
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'recipe']
    search_fields = ['user__username', 'user__email']
    empty_value_display = '-пусто-'


admin.site.unregister(Group)

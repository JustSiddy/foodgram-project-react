from django.contrib import admin

from recipes.models import (Favorites, Ingredient,
                            Recipe, ShoppingCart,
                            Tags, IngredientInRecipe)


class IngredientInRecipe(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1
    extra = 1


@admin.register(Tags)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'slug',
                    'color']
    search_fields = ['name', 'slug']
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'measurement_unit']
    search_fields = ['name']
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'author',
                    'favorite']
    list_filter = ['author', 'name', 'tags']
    search_fields = ['name', 'author__username', 'tags']
    inlines = (IngredientInRecipe,)
    empty_value_display = '-пусто-'

    def get_favorites(self, obj):
        return obj.favorite.count()
    get_favorites.short_description = 'Избранное'

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.all().value_list('name', flat=True)
        return ', '.join(ingredients)


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

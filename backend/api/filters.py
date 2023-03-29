from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Tag, Recipe

User = get_user_model()


class IngredientFilter(FilterSet):
    name = filters.CharFilter('name', 'icontains')


class RecipesFilter(FilterSet):
    author = filters.CharFilter()
    tag = filters.AllValuesMultipleFilter(
        queryset=Tag.objects.all(),
        field_name='tag__slug',
        to_field_name='slug',
    )
    is_favorited = filters.NumberFilter(
        method='get_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        fields = ['tag', 'author',
                  'is_favorited', 'is_in_shopping_cart']
        model = Recipe

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorited__user_id=user.id)
        return queryset.all()

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(in_shopping_cart__user_id=user.id)
        return queryset.all()
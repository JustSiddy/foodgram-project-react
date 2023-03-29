from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Tag, Recipe

User = get_user_model()


class IngredientFilter(FilterSet):
    name = filters.CharFilter('name', 'icontains')


class RecipesFilter(FilterSet):
    author = filters.CharFilter()
    tag = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tag__slug',
        to_field_name='slug',
    )

    is_favorited = filters.BooleanFilter(
        method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        fields = ['tag', 'author',
                  'is_favorited', 'is_in_shopping_cart']
        model = Recipe

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

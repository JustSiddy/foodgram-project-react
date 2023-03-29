from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django_filters.rest_framework import FilterSet, filters
import django_filters as filters
from recipes.models import Tag, Recipe

User = get_user_model()


class IngredientFilter(FilterSet):
    name = filters.CharFilter('name', 'icontains')


class RecipesFilter(FilterSet):
    author = filters.CharFilter()
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )

    is_favorited = filters.BooleanFilter(
        method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        fields = ['tags', 'author',
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


class TagsMultipleChoiceField(
        filters.MultipleChoiceField):
    def validate(self, value):
        if self.required and not value:
            raise ValidationError(
                self.error_messages['required'],
                code='required')
        for val in value:
            if val in self.choices and not self.valid_value(val):
                raise ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': val},)


class TagsFilter(filters.AllValuesMultipleFilter):
    field_class = TagsMultipleChoiceField

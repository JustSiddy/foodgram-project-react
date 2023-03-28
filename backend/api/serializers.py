import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient,
                            IngredientInRecipe,
                            Recipe, ShoppingCart, Tag)

from users.models import Subscription, User


class CustomUserSerializer(UserCreateSerializer):
    """Сериализер модели юзер."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ['id', 'email', 'username',
                  'first_name', 'last_name', 'is_subscribed']
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализер создания юзера."""
    class Meta:
        fields = ['first_name', 'last_name',
                  'username', 'password', 'email']
        model = User


class ShowFavoriteSerializer(serializers.ModelSerializer):
    """Сериализер отображения избранных."""
    class Meta:
        fields = ['id', 'name', 'image', 'cooking_time']
        model = Recipe


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализем модели избранное."""
    class Meta:
        fields = ['user', 'recipe']
        model = Favorite

    def to_representation(self, instance):
        return ShowFavoriteSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }
        ).data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализер модели ингредиентов."""
    class Meta:
        fields = ['id', 'name', 'measurement_unit']
        model = Ingredient


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализер модели ингредиентов в рецептах."""
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    id = serializers.ReadOnlyField(source='ingredient.id')

    class Meta:
        fields = ['id', 'name', 'amount', 'measurement_unit']
        model = IngredientInRecipe


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализер модели списка покупок."""
    class Meta:
        fields = ['user', 'recipe']
        model = ShoppingCart
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message=('Рецепт уже добавлен в список покупок.')
            )
        ]

    def to_representation(self, instance):
        return ShowFavoriteSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }
        ).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализер модели тег."""
    class Meta:
        fields = ['id', 'name',
                  'color', 'slug']
        model = Tag


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализер модели подписок."""
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta:
        fields = ['user', 'author']
        model = Subscription
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['user', 'author'],
            )

        ]

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscription.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Подписка уже оформлена.',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Подписка на самого себя - невозможна.',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipes = Recipe.objects.filter(author=obj)
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return ShowFavoriteSerializer(
            recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class DecodeImageField(serializers.ImageField):
    """Image field in Base64 encoding."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализер модели рецептов."""
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    tag = TagSerializer(many=True)
    image = DecodeImageField()

    is_favorited = SerializerMethodField(
        method_name='get_is_favorited')
    
    is_in_shopping_cart = SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    class Meta:
        fields = ['id', 'tags', 'author', 'ingredient',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time']
        model = Recipe

    def get_ingredients(self, obj):
        ingredients = IngredientInRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request').user
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    """Сериализер добавления ингредиента в рецепт."""
    id = IntegerField()
    amount = IntegerField()

    class Meta:
        fields = ['id', 'amount']
        model = IngredientInRecipe


class CreateAddRecipeSerializer(serializers.ModelSerializer):
    """Сериализер создания и обновления рецептов."""
    author = CustomUserCreateSerializer(read_only=True)
    tag = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = AddIngredientToRecipeSerializer(many=True)

    class Meta:
        fields = ['id', 'author', 'ingredients',
                  'tag', 'image', 'name', 'text',
                  'cooking_time']
        model = Recipe

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        list = []
        for i in ingredients:
            amount = i['amount']
            if int(amount) < 1:
                raise ValidationError({
                    'amount': 'Ингредиентов должно быть большое 0.'
                })
            if i['id'] in list:
                raise ValidationError({
                    'ingredients': 'Ингредиенты должны быть уникальными.'
                })
            list.append(i['id'])
        return data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, instance, validated_data):
        """Создание рецепта доступно только авторизированному пользователю."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class ShowSubscriptionSerializer(serializers.ModelSerializer):
    """ Сериализатор для отображения подписок пользователя. """

    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        fields = ['id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipe', 'recipes_count']
        model = User

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        recipes = Recipe.objects.filter(author=obj)
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return ShowFavoriteSerializer(
            recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

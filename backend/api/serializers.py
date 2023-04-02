from djoser.serializers import UserSerializer #UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorites, Ingredient, Recipe,
                            IngredientInRecipe, ShoppingCart, Tags)

from users.models import Subscription, User


# class CustomUserCreateSerializer(UserCreateSerializer): 
#     """Сериализатор создания пользователя.""" 
#     class Meta: 
#         model = User 
#         fields = ['email', 'username', 'first_name', 
#                   'last_name', 'password']


class CustomUserSerializer(UserSerializer):
    """Сериализатор модели пользователя."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed']

    def get_is_subscribed(self, obj): 
        request = self.context.get('request') 
        if request is None or request.user.is_anonymous:
            return (
                request.user.is_authenticated
                and request.user.follower.filter(user=request.user.user, author=obj.id).exists()
            )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор просмотра модели Тег."""
    class Meta:
        model = Tags
        fields = ['id', 'name', 'color', 'slug']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингредиентов в рецептах."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ['id', 'name', 'amount', 'measurement_unit']


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ингредиенты."""
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор модели Рецепт."""
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time']

    def get_ingredients(self, obj):
        ingredients = IngredientInRecipe.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def _is_exist(self, arg0, obj):
        request = self.context.get('request', None)
        return arg0.objects.filter(
            request.user.is_authenticated,
            recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        return self._is_exist(ShoppingCart, obj)

    def get_is_favorited(self, obj):
        return self._is_exist(Favorites, obj)


class CreateRecipeSerializer(serializers.ModelSerializer):
    """
    Создание рецепта.
    Обновление рецепта.
    """
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(), many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ['id', 'author', 'ingredients', 'tags',
                  'image', 'name', 'text', 'cooking_time']

    @staticmethod
    def set_recipe_ingredient(ingredients, recipe):
        ingredient_list = [
            IngredientInRecipe(
                ingredient=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount'))
            for ingredient in ingredients
        ]
        ingredient_list.sort(key=(lambda item: item.ingredient.name))
        IngredientInRecipe.objects.bulk_create(ingredient_list)

    def validate_tags(self, data):
        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                'Нужен хотя бы один тег')
        for tag in tags:
            if not Tags.objects.filter(slug=tag).exists():
                raise serializers.ValidationError(
                    'Тег не существует')

    def validate_ingredients(self, ingredients):
        ingredients_list = []
        if not ingredients:
            raise serializers.ValidationError(
                'Отсутствуют ингридиенты')
        for ingredient in ingredients:
            if ingredient['id'] in ingredients_list:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальны')
            ingredients_list.append(ingredient['id'])
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента больше 0')
        return ingredients

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время готовки должно быть не меньше одной минуты')
        return cooking_time

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        request = self.context.get('request')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.set_recipe_ingredient(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.set(tags)
        self.set_recipe_ingredient(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request')}).data


class ShowFavoriteSerializer(serializers.ModelSerializer):
    """ Сериализатор для отображения избранного. """
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class ShoppingCartSerializer(serializers.ModelSerializer):
    """ Сериализатор для списка покупок. """
    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']

    def validate(self, data):
        user = data['user']
        if user.shopping_cart.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже в списке покупок')
        return data

    def to_representation(self, instance):
        return ShowFavoriteSerializer(instance.recipe, context={
            'request': self.context.get('request')}).data


class FavoriteSerializer(serializers.ModelSerializer):
    """ Сериализатор модели Избранное. """
    class Meta:
        model = Favorites
        fields = ['user', 'recipe']

    def validate(self, data):
        user = data['user']
        if user.favorite.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже в избранном')
        return data

    def to_representation(self, instance):
        return ShowFavoriteSerializer(instance.recipe, context={
            'request': self.context.get('request')}).data


class ShowSubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор отображения подписок пользователя."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'recipes',
                  'recipes_count']

    def get_is_subscribed(self, obj): 
        request = self.context.get('request') 
        if request is None or request.user.is_anonymous:
            return (
                request.user.is_authenticated
                and request.user.follower.filter(user=request.user.user, author=obj.id).exists()
            )


    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipes = obj.recipes.all()
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return ShowFavoriteSerializer(
            recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""
    class Meta:
        model = Subscription
        fields = ['user', 'author']
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['user', 'author'])]

    def to_representation(self, instance):
        return ShowSubscriptionsSerializer(instance.author, context={
            'request': self.context.get('request')}).data

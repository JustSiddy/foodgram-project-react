from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from users.models import User


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(
        verbose_name='Название тега.',
        max_length=settings.NAME_SLUG_LENGTH)
    color = models.CharField(
        verbose_name='Цветовой HEX-код.',
        max_length=settings.COLOR_FIELD_LENGTH)
    slug = models.SlugField(
        'Slug',
        max_length=settings.NAME_SLUG_LENGTH)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        verbose_name='Название ингредиента.',
        max_length=settings.NAME_SLUG_LENGTH)
    measurement_unit = models.CharField(
        verbose_name='Единица измерения.',
        max_length=settings.NAME_SLUG_LENGTH)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_name_unit'),
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='Recipe',
        verbose_name='Автор')
    name = models.CharField(
        verbose_name='Название рецепта.',
        max_length=settings.NAME_SLUG_LENGTH)
    image = models.ImageField(
        verbose_name='Изображение.',
        upload_to='recipes/images/')
    text = models.TextField(
        verbose_name='Описание рецепта.')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты блюда')
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Ингредиенты')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(
                    1, message='Минимальное время - 1!')])
    pub_date = models.DateTimeField(
        'Время публикации.',
        auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Модель для связи ингредиентов с рецептами."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент')
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество.',
        validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'),
        ]


class FavoriteShoppingCartModel(models.Model):
    """Абстрактная модель избранного и покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(app_label)s_%(class)s_unique'),
        ]

    def __str__(self):
        return f'Пользователь {self.user}, рецепт {self.recipe}'


class Favorites(FavoriteShoppingCartModel):
    """Модель избранных рецептов."""
    class Meta(FavoriteShoppingCartModel.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        default_related_name = 'favorites'


class ShoppingCart(FavoriteShoppingCartModel):
    """Модель поукпок."""
    class Meta(FavoriteShoppingCartModel.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart'


class RecipeTag(models.Model):
    """ Модель связи тега и рецепта. """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт')
    tags = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'tags'],
                name='recipe_tag_unique'),
        ]

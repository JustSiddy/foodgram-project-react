from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (CreateRecipeSerializer, FavoriteSerializer,
                             IngredientSerializer, RecipeSerializer,
                             ShoppingCartSerializer,
                             ShowSubscriptionsSerializer,
                             SubscriptionSerializer, TagSerializer)

from recipes.models import (Favorites, Ingredient, Recipe, IngredientInRecipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User


class SubscribeView(APIView):
    """ Операция подписки/отписки. """
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        user = request.usesr
        author = get_object_or_404(User, id=id)
        data = {
            'user': user.id,
            'author': id,
        }
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(
            Subscription, user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    # def post(self, request, id):
    #     data = {
    #         'user': request.user.id,
    #         'author': id}
    #     serializer = SubscriptionSerializer(
    #         data=data,
    #         context={'request': request})
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def delete(self, request, id):
    #     author = get_object_or_404(User, id=id)
    #     if Subscription.objects.filter(
    #        user=request.user, author=author).exists():
    #         subscription = get_object_or_404(
    #             Subscription, user=request.user, author=author)
    #         subscription.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     return Response(status=status.HTTP_400_BAD_REQUEST)


class ShowSubscriptionsView(ListAPIView):
    """Отображение подписок."""
    permission_classes = [IsAuthenticated]
    pagination_class = LimitPageNumberPagination

    def get(self, request):
        user = request.user
        queryset = User.objects.filter(author__user=user)
        page = self.paginate_queryset(queryset)
        serializer = ShowSubscriptionsSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Отображение тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Отображение ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ['^name']
    pagination_class = None
    filter_backends = [IngredientFilter]


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Все действия с рецептами.
    все децствия с корзиной и избранными.
    """
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    pagination_class = LimitPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateRecipeSerializer

    def post_method_actions(self, request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_method_actions(self, request, pk, model):
        get_object_or_404(model,
                          user=request.user,
                          recipe=get_object_or_404(Recipe, id=pk)).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST"],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self.post_method_actions(
            request=request, pk=pk, serializers=FavoriteSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_method_actions(
            request=request, pk=pk, model=Favorites)

    @action(detail=True, methods=["POST"],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        return self.post_method_actions(
            request=request, pk=pk, serializers=ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def delete_shoping_cart(self, request, pk):
        return self.delete_method_actions(
            request=request, pk=pk, model=ShoppingCart)

    @staticmethod
    def send_message(ingredients):
        shopping_list = 'Купить в магазине:'
        for ingredient in ingredients:
            shopping_list += (
                f"\n{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}")
        file = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user).order_by(
            'ingredient__name').values(
            'ingredient__name',
            'ingredient__measurement_unit').annotate(amount=Sum('amount'))
        return self.send_message(ingredients)

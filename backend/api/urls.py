from django.urls import include, path
from rest_framework import routers

from .views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                    FavoriteView, ShoppingCartViewSet, ShowSubscriptionsView,
                    SubscribeView, download_shopping_cart)

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tag', TagViewSet, basename='tags')


urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('users/<int:id>/subscribe/',
         SubscribeView.as_view, name='subscribe'),
    path('users/subscriptions/',
         ShowSubscriptionsView.as_view, name='subscriptions'),
    path('recipes/<int:id>/favorite',
         FavoriteView.as_view, name='favorite'),
    path('recipes/<int:id>/shopping_cart/',
         ShoppingCartViewSet.as_view, name='shopping_cart'),
    path('recipes/download_shopping_cart/',
         download_shopping_cart,
         name='download_shopping_cart'),
]

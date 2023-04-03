from django.urls import include, path 
from rest_framework.routers import DefaultRouter 
 
from api.views import (IngredientViewSet, RecipeViewSet, 
                       ShowSubscriptionsView, SubscribeView, 
                       TagViewSet) 
 
app_name = 'api' 
 
router = DefaultRouter() 
 
router.register('ingredients', IngredientViewSet, basename='ingredients') 
router.register('recipes', RecipeViewSet, basename='recipes') 
router.register('tags', TagViewSet, basename='tags') 

userpatterns = [
    path( 
        'users/<int:id>/subscribe/', 
        SubscribeView.as_view(), 
        name='subscribe'), 
    path( 
        'users/subscriptions/', 
        ShowSubscriptionsView.as_view(), 
        name='subscriptions'), 
]

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')), 
    path('', include('djoser.urls')), 
    path('', include(router.urls)),
    path('users/', include(userpatterns))
]

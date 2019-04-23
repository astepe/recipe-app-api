from django.urls import path, include
# DRF feature that will automatically generate the urls for our viewset
# a viewset is a set of related views. You might have multiple urls associated
# with the viewset.
# e.g. /api/recipe/tags/ or /api/recipe/tags/1/
# DefaultRouter will registers the appropriate urls for all of the actions in
# our viewset
from rest_framework.routers import DefaultRouter

from recipe import views


router = DefaultRouter()

# This will then generate the appropriate urls for each view
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)

app_name = 'recipe'

urlpatterns = [
    # now all urls generated will be included in url patterns for the recipe
    # app
    path('', include(router.urls)),
]

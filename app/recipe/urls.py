"""
URL Mappings for the recipe app.
"""

from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from recipe import views

""" Default Router Creates all the different URL/routes for the all the
different options available for that viewset """
router = DefaultRouter()
router.register('recipes', views.RecipeViewSet)
router.register('tags', views.TagViewSet)

# Used for reverse mapping
app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]

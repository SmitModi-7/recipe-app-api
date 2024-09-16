"""
Views for the recipe APIs.
"""

from core.models import Recipe
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class RecipeViewSet(viewsets.ModelViewSet):
    """Handles Logic for Recipe APIs. / View for manage recipe APIs."""

    # Objects available for this viewset
    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailSerializer
    # Token Authentication
    authentication_classes = [TokenAuthentication]
    # Permissions that authenticated users have in the system
    permission_classes = [IsAuthenticated]

    """ Overiding getquery set method to filter the recipes for
    authenticated user"""
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    """ Overriding this method as we have different serializer for
    list and detail view"""
    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            self.serializer_class = RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""

        """When a new recipe is created then assigning authencticated user
        to that recipe"""
        serializer.save(user=self.request.user)

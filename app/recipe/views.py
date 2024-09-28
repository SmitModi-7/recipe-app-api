"""
Views for the recipe APIs.
"""

from core.models import (
    Recipe,
    Tag,
    Ingredient
)

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeImageSerializer
)

from rest_framework import (
    viewsets,
    mixins,
    status
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


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
        elif self.action == 'upload_image':
            # Custom Action
            self.serializer_class = RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""

        """When a new recipe is created then assigning authencticated user
        to that recipe"""
        serializer.save(user=self.request.user)

    """Creating a custom upload action which only accepts POST request,
    detail = True - The action applies to a single instance
    url_path - URL segment for this action"""
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe."""

        """ get_object() - Retrieves the instance based on pk from the URL
        (also performs authentication checks) """
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseRecipeAttrViewSet(mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):

    """Base viewset for recipe attributes."""
    # Token Authentication
    authentication_classes = [TokenAuthentication]
    # Permissions that authenticated users have in the system
    permission_classes = [IsAuthenticated]

    """ Overiding getquery set method to filter the Tags/Ingredients for
    authenticated user """
    def get_queryset(self):
        """Retrieve Tags/Ingredients for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""

    # Objects available for this viewset
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage Ingredients in the database"""

    # Objects available for this viewset
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

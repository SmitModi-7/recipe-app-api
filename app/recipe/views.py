"""
Views for the recipe APIs.
"""

from core.models import (
    Recipe,
    Tag,
    Ingredient
)

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
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


# extend schema view decorator allows us to extned our schema view
@extend_schema_view(
    # Defining list here as we want to extend schema for list endpoint.
    list=extend_schema(
        # List of parameters that can be passed through request
        parameters=[
            OpenApiParameter(
                'tags',             # Name to pass to request to filter
                OpenApiTypes.STR,   # Expects string type values
                description='Comma separated list of tag IDs to filter'
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter'
            )
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""

    # Objects available for this viewset
    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailSerializer
    # Token Authentication
    authentication_classes = [TokenAuthentication]
    # Permissions that authenticated users have in the system
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        return [int(str_id) for str_id in qs.split(',')]

    """ Overiding getquery set method to filter the recipes for
    authenticated user"""
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        # Method - 1 to get tags and ingredients
        # tags = self.request.GET.get('tags')
        # ingredients = self.request.GET.get('ingredients')

        # Method - 2 to get tags and ingredients
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        # Taking queryset in variable as we need to filter the queryset
        queryset = self.queryset
        if tags:
            # Converting comma separated string tag ids to int
            tags_id = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tags_id)
        if ingredients:
            # Converting comma separated string ingredient ids to int
            ingredients_id = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredients_id)

        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

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


# extend schema view decorator allows us to extned our schema view
@extend_schema_view(
    # Defining list here as we want to extend schema for list endpoint.
    list=extend_schema(
        # List of parameters that can be passed through request
        parameters=[
            OpenApiParameter(
                'assigned_only',    # Name to pass to request to filter
                # Only int values can be assigned to the parameter (0 or 1)
                OpenApiTypes.INT, enum=[0, 1],
                description=""" Filter by items assigned to recipes.
                            \n 0 = Filter All Tags/Ingredients
                            \n 1 = Filter Tags/Ingredients assigned to recipe
                            """
            )
        ]
    )
)
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
        """Retrieve/Filter Tags/Ingredients for authenticated user."""

        """ Getting the value of assigned only based on which
        the filter will be applied. """
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset

        """Applying filter to remove the recipes who does not
        have any tags/ingredients assigned to it"""
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()


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

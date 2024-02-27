"""
Views for the recipe APIs.
"""


from drf_spectacular.utils import(
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
    mixins,
    status,
)

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe,Tag,Ingredient
from recipe import serializers


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of tag IDs to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter',
            ),
        ]
    )
)

class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe API's."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated,]


    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        return [int(str_id) for str_id in qs.split(',')]


    def get_queryset(self):
        """Return objects for the current authenticated user only."""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()


    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.RecipeSerializer
        elif self.action =='upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """
        Upload an image to recipe.

        This method is decorated with the @action decorator to create a custom
        action for the viewset. It allows uploading an image to a specific recipe.
        """
        # Retrieve the recipe object based on the provided primary key
        recipe = self.get_object()

        # Get the serializer for the recipe instance and initialize it with the request data
        serializer = self.get_serializer(recipe, data=request.data)

        # Check if the serializer is valid (i.e., if the provided data is valid)
        if serializer.is_valid():
            # Save the serializer data to update the recipe with the uploaded image
            serializer.save()

            # Return a success response with the serialized data and status code 200 OK
            return Response(serializer.data, status=status.HTTP_200_OK)

        # If the serializer is not valid, return an error response with the serializer errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Mixins in Django are classes that provide additional functionality to views.
# They encapsulate common functionalities that can be shared across different views. Mixins are widely used in Django to promote code reuse and maintainability.
# ListModelMixin: A mixin that provides a list() method for listing objects. It's commonly used with generic views.
# UpdateModelMixin: A mixin that provides an update() method for updating an object instance. It's commonly used with generic views.

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to recipes.',
            ),
        ]
    )
)
class BaseRecipeAttrViewSet(
    mixins.DestroyModelMixin,  # Mixin for handling DELETE requests
    mixins.UpdateModelMixin,   # Mixin for handling PUT requests
    mixins.ListModelMixin,     # Mixin for handling GET requests
    viewsets.GenericViewSet    # Generic ViewSet to combine mixins
    ):
    """Base viewset for recipe attributes"""
    authentication_classes = [TokenAuthentication,]  # Authentication classes for the view
    permission_classes = [IsAuthenticated,]          # Permissions required for the view

    def get_queryset(self):
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()
        # The queryset is filtered based on the user making the request and ordered by name.
        """Filter queryset to authenticated user."""
        # Filter the queryset to include only tags of the authenticated user
        return self.queryset.filter(user=self.request.user).order_by('-name')
        # The queryset is filtered based on the user making the request and ordered by name.





class TagViewSet(BaseRecipeAttrViewSet):

    """Manage tags in the database."""

    serializer_class = serializers.TagSerializer  # Serializer for Tag model
    queryset = Tag.objects.all()                   # Queryset containing all Tag objects



class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()


















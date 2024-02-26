"""
Views for the recipe APIs.
"""

from rest_framework import (
    viewsets,
    mixins,
)

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe,Tag,Ingredient
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe API's."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        """Return objects for the current authenticated user only."""
        return self.queryset.filter(user=self.request.user).order_by('-id')


    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

# Mixins in Django are classes that provide additional functionality to views.
# They encapsulate common functionalities that can be shared across different views. Mixins are widely used in Django to promote code reuse and maintainability.
# ListModelMixin: A mixin that provides a list() method for listing objects. It's commonly used with generic views.
# UpdateModelMixin: A mixin that provides an update() method for updating an object instance. It's commonly used with generic views.


class TagViewSet(
    mixins.DestroyModelMixin,  # Mixin for handling DELETE requests
    mixins.UpdateModelMixin,   # Mixin for handling PUT requests
    mixins.ListModelMixin,     # Mixin for handling GET requests
    viewsets.GenericViewSet    # Generic ViewSet to combine mixins
):

    """Manage tags in the database."""

    serializer_class = serializers.TagSerializer  # Serializer for Tag model
    queryset = Tag.objects.all()                   # Queryset containing all Tag objects
    authentication_classes = [TokenAuthentication,]  # Authentication classes for the view
    permission_classes = [IsAuthenticated,]          # Permissions required for the view

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        # Filter the queryset to include only tags of the authenticated user
        return self.queryset.filter(user=self.request.user).order_by('-name')
        # The queryset is filtered based on the user making the request and ordered by name.


class IngredientViewSet(mixins.DestroyModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')

















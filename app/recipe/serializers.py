"""
Serializers for recipe APIs
"""

from core.models import (
    Recipe,
    Tag,
    Ingredient
)

from rest_framework import serializers


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredients."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    # many = true means it will contain list of items/tags
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link',
                  'tags', 'ingredients']
        read_only_fields = ['id']

    """ Using _ at the beginning of function name just to differentiate between
    inbuild funtion and our created funtion / This is a internal method which
    should not be called with the help of serializer. """
    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""

        # Context of the request is passed by the serializer to the view
        auth_user = self.context['request'].user
        for tag in tags:
            """ Get or create gets the value/Retrieves tags if it already exists
            or it creates new value """
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )
            recipe.tags.add(tag_obj)

    """ Using _ at the beginning of function name just to differentiate between
    inbuild funtion and our created funtion / This is a internal method which
    should not be called with the help of serializer. """
    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed."""

        # Context of the request is passed by the serializer to the view
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            """ Get or create gets the value/Retrieves tags if it already exists
            or it creates new value """
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient
            )
            recipe.ingredients.add(ingredient_obj)

    """Overiding the default create model as we need to save tags as well but
    by default when we use nested seriailizer/objects they are read only."""
    def create(self, validated_data):
        """Create a recipe."""

        """ If tags/ingredients exists in validated data then pop the tags and
        take it in new variable and if it does not exists then return
        empty list"""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])

        # Creating a recipe
        # Mehtod - 1
        """ recipe = Recipe.objects.create(**validated_data)
                                #need to pass unpacked dict """
        # Method 2
        # passing dictionary as a argument/not as individual arguments.
        recipe = super().create(validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update recipe."""

        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        super().update(instance, validated_data)

        if tags is not None:
            """ Clearing all previous tags when we update tags and create
            new ones """
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if ingredients is not None:
            """ Clearing all previous ingredients when we update ingredients
            and create new ones """
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipies with more detail about each recipe"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description', 'image']


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}

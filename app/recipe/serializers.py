"""
Serializers for recipe APIs
"""

from core.models import Recipe, Tag

from rest_framework import serializers


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    # many = true means it will contain list of items/tags
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id']

    """ Using _ at the beginning of function name just to differentiate between
    inbuild funtion and our created funtion """
    def _get_or_create_tags(self, tags, recipe):
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

    """Overiding the default create model as we need to save tags as well but
    by default when we use nested seriailizer/objects they are read only."""
    def create(self, validated_data):
        """Create a recipe."""

        """ If tags exists in validated data then pop the tags and take it in
        new variable and if it does not exists then return empty list"""
        tags = validated_data.pop('tags', [])

        # Creating a recipe
        # Mehtod - 1
        """ recipe = Recipe.objects.create(**validated_data)
                                #need to pass unpacked dict """
        # Method 2
        # passing dictionary as a argument/not as individual arguments.
        recipe = super().create(validated_data)
        self._get_or_create_tags(tags, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update recipe."""

        tags = validated_data.pop('tags', None)
        super().update(instance, validated_data)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipies with more detail about each recipe"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']

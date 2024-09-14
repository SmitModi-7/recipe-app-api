"""
Serializers for the user API View.
"""

from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user objects."""

    class Meta:
        # This represents the model which this serializer respresents.
        model = get_user_model()

        """ Fields which are needed to be serialized/created or set when we make
        a request and this will be saved in database """
        fields = ['email', 'password', 'name']

        """ We want password to be write only as we don't want password to be
        returned in our reponse due to security reasons """
        # Extra MetaData
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    """Override the behaviour of serializer (as default behaviour of serializer
    will save password as clear text instead of encrypted password )"""
    # This method will only be called when data is validated succesfully
    def create(self, validated_data):
        """Create and return user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    # Override the update method, to handle same issue as create method
    def update(self, instance, validated_data):
        """Update and return user."""

        # Removing clear text password from validated data (Defualt is None)
        password = validated_data.pop('password', None)
        # Updating user data
        user = super().update(instance, validated_data)

        # If password is updated then set and save the password
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        # When we input the text it will be hidden
        style={'input_type': 'password'},
        # White space will also be considered in password
        trim_whitespace=False
    )

    def validate(self, attrs):
        """ Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        # Authenticating username and password entered by user
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )

        # If user is not found then raise validation
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

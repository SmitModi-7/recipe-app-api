"""
Views for the user API.
"""

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import generics, authentication, permissions
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for the user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated User"""
    serializer_class = UserSerializer
    # Token Authentication
    authentication_classes = [authentication.TokenAuthentication]
    # Permissions that authenticated users have in the system
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retreive and return the authenticated user."""
        return self.request.user

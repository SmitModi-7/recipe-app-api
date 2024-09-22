"""
Database Models
"""

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models


class UserManager(BaseUserManager):
    """ Manager for users. (Manages the user model) """

    # Creating new users
    def create_user(self, email, password=None, **extra_fields):

        # Raise Value Error if email is none or empty
        if not email:
            raise ValueError('User with empty email cannot be created')

        # Creating user
        ''' self.model will take reference of the model
            our manager is associated with '''
        user = self.model(
            # Storing normalized email to maintain consistency
            email=self.normalize_email(email), **extra_fields
        )
        # Setting the hashed/encrypted user password
        user.set_password(password)
        ''' Saving user (self._db is passed to support multiple databases)
            self_.db ensures that if there are multiple database then data
            correct database is used '''
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email=email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    email = models.EmailField(unique=True, max_length=255)
    name = models.CharField(max_length=255)
    # By default the user will be active
    is_active = models.BooleanField(default=True)
    # For giving permission to admin section
    is_staff = models.BooleanField(default=False)

    # Assigning user manager
    objects = UserManager()

    # Authentication for users will work on email instead of username
    USERNAME_FIELD = 'email'

    # String Representation of our model
    def __str__(self):
        return self.email


class Tag(models.Model):
    """Tag Model for storing tags for recipes"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredients for recipes."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe Model"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    # Many Different recipes may have many different tags
    tags = models.ManyToManyField(Tag)
    # Many Different recipes may have many different ingredients
    ingredients = models.ManyToManyField(Ingredient)

    def __str__(self):
        return self.title

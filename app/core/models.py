from django.db import models

# for extending and customizing user models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.conf import settings


class UserManager(BaseUserManager):
    """Provides helper functions for creating a user or superuser
    Here we are overriding BaseUserManager to handle email address
    intead of username that it expects. """

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user to database"""

        if not email:
            raise ValueError('Users must have an email address')

        # create user # normalize_email is a built-int django function that
        # will normalize an email string
        user = self.model(email=self.normalize_email(email), **extra_fields)

        # using the built in django password method
        user.set_password(password)

        # using=self._db used for supporting multiple databases. Not
        # using here but it is good practice to use it anyway.
        user.save(using=self._db)

        # return user model object
        return user

    def create_superuser(self, email, password):
        """Creates and saves a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username.
    AbstractBaseUser give us all the django user model features which allows
    us to then override attributes to customize our models"""

    # later this field will be the one that overrides the required username
    # field
    email = models.EmailField(max_length=255, unique=True)

    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # overriding the objects attribute and setting it to the UserManager
    objects = UserManager()

    # overriding the required USERNAME_FIELD attribute which by default is set
    # to 'username'. Here we set it to 'email'. This attribute is defined at
    # the top
    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """Tag to be used for a recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        # this parameter we defined in app/setting.py, the model it will be
        # linked to
        settings.AUTH_USER_MODEL,
        # this will automatically delete the tag if the user was also deleted
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient to be used in a recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.title

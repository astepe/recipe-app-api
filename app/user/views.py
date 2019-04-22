from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    # this class will handle all of the incoming requests. It will both
    # validate and serialize the request data into Python objects
    # We are using the serializer that we defined which corresponds to the
    # User model
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    # this is where the authentication happens. This class will take care of
    # getting the authenicated user by using the incoming request object.
    # this will create self.request which will contain the user.
    # self.request.user
    authentication_classes = (authentication.TokenAuthentication, )
    # this defines the level of access that the user will have
    permission_classes = (permissions.IsAuthenticated, )

    # overriding base class method to just return the user
    def get_object(self):
        """Retrieve the authenticated user object"""
        return self.request.user

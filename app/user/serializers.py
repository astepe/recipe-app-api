from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """serializer for the users object"""

    class Meta:
        # this will generate the fields for the serializer based on our custom
        # User model as well as include all validators
        model = get_user_model()

        # define the fields from the model that we want to use
        fields = ('email', 'password', 'name')

        # This will add extra parameters to the password CharField field
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update the user, setting the password correctly and return it"""
        # instance = model instance that is linked to the model serializer
        # validated_data = the fields defined in Meta that have been validated
        password = validated_data.pop('password', None)
        # after we remove the password, we can call the parent class .update
        # method.
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        # attrs will be every field that makes up the current serializer
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            # context is passed into the serializer when a request is made
            # this is how we can get access to the request itself
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs

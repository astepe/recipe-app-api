from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# test framework for making requests to our api and check responses
from rest_framework.test import APIClient

# contains status codes in human-readable format
from rest_framework import status


# constant variable for test url
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


# helper function to get the user model
def create_user(**params):
    return get_user_model().objects.create_user(**params)


# public APIs are just apis that aren't authenticated
class PublicUsersAPITests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    # all tests will use a new and refreshed instance of the database so
    # we don't need to worry about not using the same data in each test
    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        # payload is the object that you pass to the api when you make
        # the request
        payload = {
            'email': 'test@test.com',
            'password': 'testpass',
            'name': 'Test name',
        }
        # user should get created and saved to database when request is made
        response = self.client.post(CREATE_USER_URL, payload)

        # check that the request was successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check that the user was saved to the database by trying to get it
        user = get_user_model().objects.get(**response.data)

        # check that the password is correct
        self.assertTrue(user.check_password(payload['password']))

        # check that the password was not sent with the response. This could be
        # a potential security vulnerability
        self.assertNotIn('password', response.data)

    def test_user_exists(self):
        """Test creating a user that already exists FAILS"""
        payload = {'email': 'test@test.com', 'password': 'testpass'}

        # create and save user to db
        create_user(**payload)

        # then when the post request is made it must fail
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {'email': 'test@test.com', 'password': 'pw'}
        response = self.client.post(CREATE_USER_URL, payload)

        # not only do we check that the server returned a 400, but that the
        # user was ALSO NOT saved to database
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {'email': 'ari@test.com', 'password': 'testpass'}
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email='test@test.com', password='testpass')
        payload = {'email': 'test@if invalid credenttest.com',
                   'password': 'wrong'}
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""
        payload = {'email': 'test@test.com', 'password': 'testpass'}
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        response = self.client.post(TOKEN_URL,
                                    {'email': 'one', 'password': ''})

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is requried for users"""
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUsersAPITests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        payload = {'email': 'ari@test.com', 'password': 'testpass'}
        self.user = create_user(**payload)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test that post is not allowed on the me url"""
        response = self.client.post(ME_URL, {})

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test that the user can update profile for auth user"""
        payload = {'name': 'new name', 'password': 'newpass123'}
        response = self.client.patch(ME_URL, payload)

        # updated user with latest values from database. Basically get the
        # updated information from the database and set it to the user object
        self.user.refresh_from_db()

        # verify updates were made by comparing to payload
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

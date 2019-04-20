from django.test import TestCase
from django.contrib.auth import get_user_model

# allows us to generate urls for admin page
from django.urls import reverse

# test client that allows us to make test requests to our application
from django.test import Client


class AdminSiteTests(TestCase):

    # setup function. Similar to pytest fixtures
    def setUp(self):
        # create test client
        self.client = Client()
        # make a new user
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@test.com',
            password='password123'
        )
        # make sure user is logged in. This is nice because it means that
        # we don't need to manually log the user in each time we execute a test
        self.client.force_login(self.admin_user)
        # create a regular user that isnt authenticated to list on our admin
        # page

        self.user = get_user_model().objects.create_user(
            email='testuser@test.com',
            password='password',
            name='Test user full name'
        )

    def test_users_listed(self):
        """Test that users are listed on user page"""
        # urls are defined in django similar to url_for in flask
        url = reverse('admin:core_user_changelist')

        # make an http GET on url with logged in admin_user
        response = self.client.get(url)

        # also checks that http response was 200 code
        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def test_user_change_page(self):
        """user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        # /admin/core/user/1

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_create_user_page(self):
        """Test create user page works"""
        url = reverse('admin:core_user_add')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

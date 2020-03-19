from django.test import TestCase

# Create your tests here.
import os
import re

import explore_scotland_app.models
from explore_scotland_app import forms

from django.db import models
from django.test import TestCase
from django.conf import settings
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.forms import fields as django_fields

from explore_scotland_app.populate_explore_scotland_app import populate

FAILURE_HEADER = f"{os.linesep}{os.linesep}{os.linesep}================{os.linesep}TwD TEST FAILURE =({os.linesep}================{os.linesep}"
FAILURE_FOOTER = f"{os.linesep}"

f"{FAILURE_HEADER} {FAILURE_FOOTER}"


class LoginTests(TestCase):
	def setUp(self):
		populate()
		
    def test_login_functionality(self):
        """
        Tests the login functionality. A user should be able to log in, and should be redirected to homepage.
        """
        user = User.objects.get(username='cindy')
        response = self.client.post(reverse('explore_scotland_app:login'), {'username': 'cindy', 'password': 'testcindy3'})
        try:
            self.assertEqual(user.id, int(self.client.session['_auth_user_id']),
                             f"{FAILURE_HEADER}We attempted to log a user in with an ID of {user.id}, but instead logged a user in with an ID of {self.client.session['_auth_user_id']}.{FAILURE_FOOTER}")
        except KeyError:
            self.assertTrue(False,
                            f"{FAILURE_HEADER}When attempting to log in with login() view, it didn't seem to log the user in. {FAILURE_FOOTER}")

        self.assertEqual(response.status_code, 302,
                         f"{FAILURE_HEADER}Testing login functionality, logging in was successful. However, we got a status code of {response.status_code} instead. {FAILURE_FOOTER}")

        self.assertEqual(response.url, reverse('explore_scotland_app:index'),
                         f"{FAILURE_HEADER}We were not redirected to the homepage after logging in.{FAILURE_FOOTER}")


class LogoutTests(TestCase):
    """
    Tests to check the functionality of logging out.
    """
    def setUp(self):
		populate()
		
    def test_bad_logout(self):
        """
        Attepts to log out a user who is not logged in.
        """
        response = self.client.get(reverse('explore_scotland_app:logout'))
        self.assertTrue(response.status_code, 302)
        self.assertTrue(response.url, reverse('explore_scotland_app:login'))

    def test_good_logout(self):
        """
        Attempts to log out a user who IS logged in.
        """
        self.client.login(username='cindy', password='testcindy3')

        # Now log the user out. check the redirect to the homepage.
        response = self.client.get(reverse('explore_scotland_app:logout'))
        self.assertEqual(response.status_code, 302,
                         f"{FAILURE_HEADER}Didn't  redirect logged out user to the homepage. {FAILURE_FOOTER}")
        self.assertEqual(response.url, reverse('explore_scotland_app:index'),
                         f"{FAILURE_HEADER}Didn't  redirect logged out user to the homepage. {FAILURE_FOOTER}")
        self.assertTrue('_auth_user_id' not in self.client.session,
                        f"{FAILURE_HEADER}Logging out with logout() view don't actually log the user out!{FAILURE_FOOTER}")

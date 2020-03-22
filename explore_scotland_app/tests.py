import os
import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from explore_scotland_app.population_script import populate
from explore_scotland_app.models import UserProfile, Photo, Comment

FAILURE_HEADER = f"{os.linesep}{os.linesep}{os.linesep}================{os.linesep}TwD TEST FAILURE =({os.linesep}================{os.linesep}"
FAILURE_FOOTER = f"{os.linesep}"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DIR = os.path.join(BASE_DIR, 'media/test')
TEST_TEMP_DIR = os.path.join(BASE_DIR, 'media/test/temp')


def create_user_profile():
    """
    Helper function to create a User Profile.
    """
    user = User.objects.get_or_create(username='testuser', email='test@email.com')[0]
    user.set_password('testpassword')
    user.save()
    user_profile = \
        UserProfile.objects.get_or_create(user=user, picture=tempfile.NamedTemporaryFile(suffix=".jpg").name)[0]
    user_profile.save()

    return user_profile


def create_super_user():
    """
    Helper function to create a super user.
    """
    return User.objects.create_superuser('admin', 'admin@email.com', 'testadminpassword')


class RegisterTests(TestCase):

    def test_blank_registration_post(self):
        """
        Checks the POST response of the registration view when submit a blank form
        """
        request = self.client.post(reverse('explore_scotland_app:register'))
        content = request.content.decode('utf-8')

        self.assertTrue('<ul class="errorlist">' in content)

    @override_settings(MEDIA_ROOT=(TEST_TEMP_DIR + '/media'))
    def test_good_registration_post(self):
        """
        checks the functionality of registration.
        create a good POST response of the registration view.
        """
        img = open(TEST_DIR + '/cindy.jpg', 'rb')

        post_data = {'username': 'testuser', 'email': 'test@email.com', 'password': 'testpassword', 'picture': img}
        request = self.client.post(reverse('explore_scotland_app:register'), post_data)

        content = request.content.decode('utf-8')

        self.assertTrue(self.client.login(username='testuser', password='testpassword'),
                        f"{FAILURE_HEADER}We couldn't log in the user we created using your registration form. Please check your implementation of the register() view. Are you missing a .save() call?{FAILURE_FOOTER}")
        self.assertTrue('<a href="/">Return to the homepage.</a>' in content,
                        f"{FAILURE_HEADER}After successfully registering, we couldn't find the expected link back to the homepage.{FAILURE_FOOTER}")

    @override_settings(MEDIA_ROOT=(TEST_TEMP_DIR + '/media'))
    def test_duplicated_registration_post(self):
        """
        create a existed user of the registration view.
        """
        img = open(TEST_DIR + '/cindy.jpg', 'rb')
        create_user_profile()
        post_data = {'username': 'testuser', 'password': 'testpassword', 'email': 'test@email.com', 'picture': img}
        request = self.client.post(reverse('explore_scotland_app:register'), post_data)
        content = request.content.decode('utf-8')
        # print(content)
        self.assertTrue('<a href="/login/"' in content,
                        f"{FAILURE_HEADER}After repeated registering, we couldn't find the expected link back to the log in page.{FAILURE_FOOTER}")


class LoginTests(TestCase):
    def setUp(self):
        populate()

    def test_login_functionality(self):
        """
        Tests the login functionality. A user should be able to log in, and should be redirected to homepage.
        """
        user = User.objects.get(username='cindy')
        response = self.client.post(reverse('explore_scotland_app:login'),
                                    {'username': 'cindy', 'password': 'testcindy3'})
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

    def test_good_request_login_required_links(self):
        """
        Tests to visit log in required pages when logged in
        """
        self.client.login(username='cindy', password='testcindy3')
        responses = []
        restricted_pages = ['explore_scotland_app:edit_profile', 'explore_scotland_app:upload_photo',
                            'explore_scotland_app:profile']
        for p in restricted_pages:
            responses.append(self.client.get(reverse(p)))

        for response in responses:
            self.assertEqual(response.status_code, 200,
                             f"{FAILURE_HEADER}we cannot visit login required page while logging in{FAILURE_FOOTER}")


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

    def test_bad_request_login_required_links(self):
        """
        Tests to visit log in required pages when logged out
        """

        responses = []
        restricted_pages = ['explore_scotland_app:edit_profile', 'explore_scotland_app:upload_photo',
                            'explore_scotland_app:profile']
        for p in restricted_pages:
            responses.append(self.client.get(reverse(p)))

        for response in responses:
            self.assertEqual(response.status_code, 302,
                             f"{FAILURE_HEADER}we can visit login required page while logged out{FAILURE_FOOTER}")


class TestEditProfile(TestCase):
    def test_edit_profile_post(self):
        """
        test updating a username using edit_profile
        """
        populate()
        self.client.login(username='cindy', password='testcindy3')

        profile_data = {'username': 'django', 'email': 'changed@email.com'}
        self.client.post(reverse('explore_scotland_app:edit_profile'), profile_data)

        user_id = int(self.client.session['_auth_user_id'])
        user = User.objects.get(id=user_id)

        self.assertEqual(profile_data.get('username'), user.username,
                         f"{FAILURE_HEADER}filed to edit username through editprofile{FAILURE_FOOTER}")
        self.assertEqual(profile_data.get('email'), user.email,
                         f"{FAILURE_HEADER}filed to edit email through editprofile{FAILURE_FOOTER}")


class TestEditPhotos(TestCase):
    """
    test edit/add photo functionalities
    """

    def setUp(self):
        populate()

    def test_add_photo_link_presents(self):
        """
        check whether link of upload photo exists
        """
        self.client.login(username='cindy', password='testcindy3')
        content = self.client.get(reverse('explore_scotland_app:profile')).content.decode()
        # print(content)
        self.assertTrue('''href="/upload-photo/">Upload Photo</a>''' in content,
                        f"{FAILURE_HEADER}add photo link does not exist on detail page{FAILURE_FOOTER}")

    @override_settings(MEDIA_ROOT=(TEST_TEMP_DIR + '/media'))
    def test_add_photo_post(self):
        """
        check the functionality of upload photo
        view and data in model checked
        """
        self.client.login(username='cindy', password='testcindy3')

        pic = open(TEST_DIR + '/test_photo.jpg', 'rb')
        photo_data = {'picture': pic, 'description': 'My beloved uni', 'categories': 'PP', 'tags': 'cindy'}

        response = self.client.post(reverse('explore_scotland_app:upload_photo'), photo_data)
        content = self.client.get(reverse('explore_scotland_app:profile')).content.decode()
        photo = Photo.objects.filter(description='My beloved uni')[0]

        # print(content)
        self.assertTrue('''<img class="border rounded mw-100" src='/media/test_photo.jpg'/>''' in content)
        self.assertEqual(photo.tags, 'cindy',
                         f"{FAILURE_HEADER}The new photo uploaded didn't have the tag we specified{FAILURE_FOOTER}")

    def test_edit_photo_link_presents(self):
        """
        check whether the edit photo link exists for photo owner
        """
        photo = Photo.objects.filter(description='train with smoke')[0]
        self.client.login(username='bob', password='testbob2')

        response = self.client.get(reverse('explore_scotland_app:picture_details', kwargs={'photo_id': photo.id}))
        content = response.content.decode()
        # print(content)
        self.assertTrue('href="/edit-photo/' + str(photo.id) + '">Edit</a>' in content,
                        f"{FAILURE_HEADER}edit photo link not presents for the photo owner{FAILURE_FOOTER}")

    def test_edit_photo_link_not_presents(self):
        """
        check whether the edit photo link exists for nonowner
        """
        photo = Photo.objects.filter(description='train with smoke')[0]
        self.client.login(username='cindy', password='testcindy3')

        response = self.client.get(reverse('explore_scotland_app:picture_details', kwargs={'photo_id': photo.id}))
        content = response.content.decode()

        self.assertTrue('href="/edit-photo/' + str(photo.id) + '">Edit</a>' not in content,
                        f"{FAILURE_HEADER}edit photo link presents for non photo owner{FAILURE_FOOTER}")

    def test_edit_photo_post(self):
        """
        test the functionality of edit photo
        display and model checks
        """
        photo = Photo.objects.filter(description='train with smoke')[0]
        self.client.login(username='bob', password='testbob2')
        photo_data = {'description': 'the mountain', 'categories': 'LS', 'tags': 'highland'}

        response = self.client.post(reverse('explore_scotland_app:edit_photo', kwargs={'photo_id': photo.id}),
                                    photo_data)
        content = self.client.get(
            reverse('explore_scotland_app:picture_details', kwargs={'photo_id': photo.id})).content.decode()
        pic = Photo.objects.get(id=photo.id)

        self.assertTrue(photo_data['description'] in content,
                        f"{FAILURE_HEADER}The new photo updated didn't display the description we update{FAILURE_FOOTER}")
        self.assertEqual(pic.tags, 'highland',
                         f"{FAILURE_HEADER}The new photo updated didn't have the tag we update in models{FAILURE_FOOTER}")

    def test_like_photo(self):
        """
        test the functionality of like photo
        model checks
        display in profile page checks
        """
        photo = Photo.objects.filter(description='train with smoke')[0]
        user = User.objects.filter(username='alice')[0]
        self.client.login(username='alice', password='testalice1')

        self.client.get(reverse('explore_scotland_app:like_photo', kwargs={'photo_id': photo.id}))

        self.assertTrue(user.profile in photo.likes.all(),
                        f"{FAILURE_HEADER}data in model didn,t update after we like a photo{FAILURE_FOOTER}")

        content = self.client.get(reverse('explore_scotland_app:profile')).content.decode()

        self.assertTrue('''src='/media/test/train.jpg'/>''' in content,
                        f"{FAILURE_HEADER}profile page didn't show liked photo after we like a photo{FAILURE_FOOTER}")

    def test_dislike_photo(self):
        """
        test the functionality of cancel like photo
        model checks
        """
        photo = Photo.objects.filter(description='train with smoke')[0]
        user = User.objects.filter(username='alice')[0]
        self.client.login(username='alice', password='testalice1')

        self.client.get(reverse('explore_scotland_app:like_photo', kwargs={'photo_id': photo.id}))
        self.client.get(reverse('explore_scotland_app:like_photo', kwargs={'photo_id': photo.id}))

        self.assertTrue(user.profile not in photo.likes.all(),
                        f"{FAILURE_HEADER}data in model didn,t update after we dislike a photo{FAILURE_FOOTER}")


class TestEditComment(TestCase):

    def setUp(self):
        populate()

    def test_add_comment_link_prensents(self):
        """
        test if the add comment link presents
        """
        photo = Photo.objects.filter(description='train with smoke')[0]
        self.client.login(username='alice', password='testalice1')

        response = self.client.get(reverse('explore_scotland_app:picture_details', kwargs={'photo_id': photo.id}))
        content = response.content.decode()
        # print(content)
        self.assertTrue('' in content,
                        f"{FAILURE_HEADER}cannot find the link to add comment in the photo detail page{FAILURE_FOOTER}")

    def test_add_blank_comment_post(self):
        """
        test the functionality of add a comment to photo
        if we add a blank comment
        """
        photo = Photo.objects.filter(description='train with smoke')[0]
        self.client.login(username='cindy', password='testcindy3')

        comment_data = {'content': '  ', 'photo_id': photo.id}
        self.client.post(reverse('explore_scotland_app:post_comment', kwargs={'photo_id': photo.id}), comment_data)
        content = self.client.get(
            reverse('explore_scotland_app:picture_details', kwargs={'photo_id': photo.id})).content.decode()

        self.assertTrue('''<p class="text-center">No comments</p>''' in content,
                        f"{FAILURE_HEADER}a comment with only spaces should not be accepted{FAILURE_FOOTER}")

    def test_add_comment_post(self):
        """
        test the functionality of add a comment to photo
        checks data in model and display
        """
        photo = Photo.objects.filter(description='train with smoke')[0]
        self.client.login(username='cindy', password='testcindy3')

        comment_data = {'content': 'nice picture', 'photo_id': photo.id}
        self.client.post(reverse('explore_scotland_app:post_comment', kwargs={'photo_id': photo.id}), comment_data)
        content = self.client.get(
            reverse('explore_scotland_app:picture_details', kwargs={'photo_id': photo.id})).content.decode()
        # print(content)

        comment = Comment.objects.filter(content='nice picture')[0]
        self.assertTrue(comment is not None,
                        f"{FAILURE_HEADER}failed to add comment to photo through the post on picture_detail page{FAILURE_FOOTER}")
        self.assertTrue('''<p class="card-text">nice picture</p>''' in content,
                        f"{FAILURE_HEADER}the added photo comment didn't display well on the template{FAILURE_FOOTER}")

        """
        test the functionality of add a comment to a comment
        checks data in model and display
        """
        self.client.logout()
        self.client.login(username='bob', password='testbob2')

        comment_data = {'content': 'thank you', 'comment_id': comment.id, 'photo_id': photo.id}
        self.client.post(reverse('explore_scotland_app:post_comment', kwargs={'photo_id': photo.id}), comment_data)
        content = self.client.get(
            reverse('explore_scotland_app:picture_details', kwargs={'photo_id': photo.id})).content.decode()
        commentcomment = Comment.objects.filter(content='thank you')[0]

        self.assertTrue(commentcomment is not None,
                        f"{FAILURE_HEADER}failed to add comment to a comment through the post on picture_detail page{FAILURE_FOOTER}")
        self.assertTrue('''<p class="card-text">thank you</p>''' in content,
                        f"{FAILURE_HEADER}the added comment comment didn't display well on the template{FAILURE_FOOTER}")


def tearDownModule():
    print("\nDeleting temporary media files...\n")
    try:
        shutil.rmtree(TEST_TEMP_DIR)
    except OSError:
        pass

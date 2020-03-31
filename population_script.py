import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'explore_scotland.settings')

import django

django.setup()

from django.contrib.auth.models import User
from explore_scotland_app.models import UserProfile, Photo, Comment


def populate():
    test_users = {
        'alice': {'username': 'alice',
                  'email': 'alice1@test.com',
                  'password': 'testalice1',
                  'image': 'test/alice.jpg'},
        'bob': {'username': 'bob',
                'email': 'bob2@test.com',
                'password': 'testbob2',
                'image': 'test/bob.jpg'},
        'cindy': {'username': 'cindy',
                  'email': 'cindy3@test.com',
                  'password': 'testcindy3',
                  'image': 'test/cindy.jpg'}
    }

    test_photos = [
        {'owner': 'alice',
         'description': 'glasgow bridge',
         'cat': 'AC',
         'tag': 'glasgow bridge beauty',
         'picture': 'test/queensferry_crossing.png'},
        {'owner': 'alice',
         'description': 'glasgow university',
         'cat': 'AC',
         'tag': 'glasgow university',
         'picture': 'test/university_of_glasgow.jpg'},
        {'owner': 'bob',
         'description': 'edinburgh castle',
         'cat': 'AC',
         'tag': 'edinburgh castles royalty',
         'picture': 'test/castle_1.jpg'},
        {'owner': 'bob',
         'description': 'scottish man playing pipes',
         'cat': 'PP',
         'tag': 'man bagpipes scottish',
         'picture': 'test/scottish_piper.png'},
        {'owner': 'alice',
         'description': 'calton hill castle',
         'cat': 'AC',
         'tag': 'hill castle',
         'picture': 'test/calton_hill.jpg'},
        {'owner': 'alice',
         'description': 'castle',
         'cat': 'AC',
         'tag': 'castle',
         'picture': 'test/castle_2.jpg'},
        {'owner': 'bob',
         'description': 'scottish sunrise',
         'cat': 'LS',
         'tag': 'sunrise landscape beautiful',
         'picture': 'test/scottish_sunrise.jpg'},
        {'owner': 'bob',
         'description': 'scottish yak',
         'cat': 'LS',
         'tag': 'yak animal',
         'picture': 'test/scottish_yak.jpg'},
         
    ]

    for user, user_data in test_users.items():
        add_user(user, user_data['email'], user_data['password'], user_data['image'])

    for photo in test_photos:
        add_photo(photo['owner'], photo['description'], photo['cat'], photo['tag'], photo['picture'])


def add_user(name, email, password, image):
    u = User.objects.get_or_create(username=name, first_name='Test', last_name='User', email=email)[0]
    u.set_password(password)
    up = UserProfile.objects.get_or_create(user=u, picture=image)[0]
    u.save()
    return up


def add_photo(owner, description, cat, tag, picture):
    u = User.objects.get(username=owner)
    up = UserProfile.objects.get(user=u)
    p = Photo.objects.get_or_create(owner=up, description=description, categories=cat, tags=tag, picture=picture)
    return p


if __name__ == '__main__':
    print('Starting explore-scotland population script...')
    populate()

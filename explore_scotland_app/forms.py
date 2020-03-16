from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from explore_scotland_app.models import UserProfile, Photo, Comment

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username', 'email', 'password',)
        help_texts = {
			'username': '',
		}

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('picture',)
        
class UserFormWithoutPassword(UserForm):
    def __init__(self, *args, **kwargs):
        super(UserFormWithoutPassword, self).__init__(*args, **kwargs)
        self.fields.pop('password')
        
class PhotoForm(forms.ModelForm):
	class Meta:
		model = Photo
		fields = ('picture', 'description', 'categories', 'tags')
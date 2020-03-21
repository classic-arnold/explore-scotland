from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from explore_scotland_app.models import UserProfile, Photo, Comment

class UserForm(forms.ModelForm):
	# user form for signup
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username', 'email', 'password',)
        help_texts = {
			'username': '',
		}

class UserProfileForm(forms.ModelForm):
	# user profile form for getting user's profile picture
    class Meta:
        model = UserProfile
        fields = ('picture',)
        
class UserFormWithoutPassword(UserForm):
	# user form without password to edit details
    def __init__(self, *args, **kwargs):
        super(UserFormWithoutPassword, self).__init__(*args, **kwargs)
        self.fields.pop('password')
        
class PhotoForm(forms.ModelForm):
	# photo form to upload photo
	class Meta:
		model = Photo
		fields = ('picture', 'description', 'categories', 'tags')
		
	def __init__(self, *args, **kwargs):
		super(PhotoForm, self).__init__(*args, **kwargs)
		# add placeholder to form field
		self.fields['tags'].widget.attrs['placeholder'] = 'Separate by space'
		
class CommentForm(forms.ModelForm):
	# comment form to post comment
	class Meta:
		model = Comment
		fields = ('content',)
		labels = {
			'content': ''
		}
		
class PhotoFormWithoutPhoto(PhotoForm):
	# photo form without picture to edit photo details
	def __init__(self, *args, **kwargs):
		super(PhotoFormWithoutPhoto, self).__init__(*args, **kwargs)
		self.fields.pop('picture')
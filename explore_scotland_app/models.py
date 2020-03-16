from django.db import models

from django.core.exceptions import ValidationError

from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	picture = models.ImageField(upload_to="")
	
	def __str__(self):
		return self.user.first_name + self.user.last_name
		
class Photo(models.Model):
	owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="photos_uploaded")
	description = models.TextField(max_length=256)
	date_added = models.DateField(auto_now_add=True)
	categories = models.CharField(max_length=256) #add choice
	tags = models.CharField(max_length=256) #add choice
	likes = models.ManyToManyField(UserProfile, related_name="photos_liked")
	photo = models.ImageField(upload_to="")
	
	
	def __str__(self):
		return self.owner.user.first_name + self.owner.user.last_name + "photo"
		
class Comment(models.Model):
	owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="comment_posted")
	content = models.TextField(max_length=256)
	photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name="photo_comments", null=True, blank=True)
	comment = models.ForeignKey("self", on_delete=models.CASCADE, related_name="comment_comments", null=True, blank=True)
	date_added = models.DateField(auto_now_add=True)
	
	def clean(self):
		super().clean()
		if self.photo is None and self.comment is None:
			raise ValidationError('Comments must be linked to either a photo or a comment.')
	
	def __str__(self):
		if self.photo is not None:
			return self.owner.user.first_name + self.owner.user.last_name + "comment on" + self.photo.__str__()
		else:
			return self.owner.user.first_name + self.owner.user.last_name + "comment on" + self.comment.__str__()
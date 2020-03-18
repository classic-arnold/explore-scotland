from django.db import models

from django.core.exceptions import ValidationError

from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
	picture = models.ImageField(upload_to="")
	
	def __str__(self):
		return self.user.username
		
class Photo(models.Model):
	
	LANDSCAPE = 'LS'
	ARCHITECTURE = 'AC'
	PEOPLE = 'PP'

	CATEGORY_CHOICES = [
		(LANDSCAPE, 'Landscape'),
		(ARCHITECTURE, 'Architecture'),
		(PEOPLE, 'People'),
	]
    
	owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="photos_uploaded")
	description = models.TextField(max_length=256)
	date_added = models.DateField(auto_now_add=True)
	categories = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=LANDSCAPE)
	tags = models.CharField(max_length=256, null=True, blank=True) #add choice
	likes = models.ManyToManyField(UserProfile, related_name="photos_liked")
	picture = models.ImageField(upload_to="")
	
	class Meta:
		ordering = ('-date_added',)
	
	def __str__(self):
		return self.owner.user.username + " photo."
		
class Comment(models.Model):
	owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="comment_posted")
	content = models.TextField(max_length=256)
	photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name="photo_comments", null=True, blank=True)
	comment = models.ForeignKey("self", on_delete=models.CASCADE, related_name="comment_comments", null=True, blank=True)
	date_added = models.DateField(auto_now_add=True)
	
	def save(self):
		super().save()
		if self.photo is None and self.comment is None:
			raise ValidationError('Comments must be linked to either a photo or a comment.')
	
	def __str__(self):
		if self.photo is not None:
			return self.owner.user.username + " comment on " + self.photo.__str__()
		else:
			return self.owner.user.username + " comment on " + self.comment.__str__()
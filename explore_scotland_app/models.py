from django.db import models

from django.core.exceptions import ValidationError

from django.contrib.auth.models import User

from PIL import Image

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
	picture_square = models.ImageField(upload_to="")
	
	class Meta:
		ordering = ('-date_added',)
	
	def __str__(self):
		return self.owner.user.username + " photo."
		
	def save(self, *args, **kwargs):
		self.picture_square = self.picture
		super().save()
		img = Image.open(self.picture_square.path)
		width, height = img.size  # Get dimensions

		if width > 300 and height > 300:
			# keep ratio but shrink down
			img.thumbnail((width, height))

		# check which one is smaller
		if height < width:
			# make square by cutting off equal amounts left and right
			left = (width - height) / 2
			right = (width + height) / 2
			top = 0
			bottom = height
			img = img.crop((left, top, right, bottom))

		elif width < height:
			# make square by cutting off bottom
			left = 0
			right = width
			top = 0
			bottom = width
			img = img.crop((left, top, right, bottom))

		img.save(self.picture_square.path)
		
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
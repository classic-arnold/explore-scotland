from django.db import models

#import User

# Create your models here.
class Profile(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	profile_picture = models.ImageField(upload_to="")
	
	def __str__(self):
		return self.user.first_name + self.user.last_name
		
class Photo(models.Model):
	owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="photos_uploaded")
	description = models.TextField(max_length=256)
	
	
from .models import UserProfile
from django.core.files.base import ContentFile
from urllib.request import urlopen

def create_profile(strategy, details, response, user, backend, *args, **kwargs):
	if UserProfile.objects.filter(user=user).exists():
		pass
	else:
		new_profile = UserProfile(user=user)
	
		if backend.name == 'facebook':
			res_id = response['id']
			url = "http://graph.facebook.com/%s/picture?type=large"%res_id
			ext = 'png'
			img_name = str(user.pk)+'-image'
			new_profile.picture.save(
			   '{0}.{1}'.format(img_name, ext),
			   ContentFile(urlopen(url).read()),
			   save=False
			)
			new_profile.save()

	return kwargs
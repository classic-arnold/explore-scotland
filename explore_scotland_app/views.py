from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from explore_scotland_app.forms import UserForm, UserProfileForm, UserFormWithoutPassword, PhotoForm, CommentForm, PhotoFormWithoutPhoto
from explore_scotland_app.models import UserProfile, Photo, Comment
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

def index(request):
	return render(request, 'explore_scotland_app/index.html')

def register(request):
	# A boolean value for telling the template
	# whether the registration was successful.
	# Set to False initially. Code changes value to
	# True when registration succeeds.
	registered = False

	# If it's a HTTP POST, we're interested in processing form data.
	if request.method == 'POST':
		# Attempt to grab information from the raw form information.
		# Note that we make use of both UserForm and UserProfileForm.
		user_form = UserForm(request.POST)
		profile_form = UserProfileForm(request.POST, request.FILES)

		# If the two forms are valid...
		if user_form.is_valid() and profile_form.is_valid():
			# Save the user's form data to the database.
			user = user_form.save()

			# Now we hash the password with the set_password method.
			# Once hashed, we can update the user object.
			user.set_password(user.password)
			user.save()

			# Now sort out the UserProfile instance.
			# Since we need to set the user attribute ourselves,
			# we set commit=False. This delays saving the model
			# until we're ready to avoid integrity problems.
			profile = profile_form.save(commit=False)
			profile.user = user

			# Did the user provide a profile picture?
			# If so, we need to get it from the input form and
			#put it in the UserProfile model.
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			# Now we save the UserProfile model instance.
			profile.save()

			# Update our variable to indicate that the template
			# registration was successful.
			registered = True
	else:
		# Not a HTTP POST, so we render our form using two ModelForm instances.
		# These forms will be blank, ready for user input.
		user_form = UserForm()
		profile_form = UserProfileForm()

	# Render the template depending on the context.
	return render(request,'explore_scotland_app/register.html',context = {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
	# If the request is a HTTP POST, try to pull out the relevant information.
	if request.method == 'POST':
		# Gather the username and password provided by the user.
		# This information is obtained from the login form.
		# We use request.POST.get('<variable>') as opposed
		# to request.POST['<variable>'], because the
		# request.POST.get('<variable>') returns None if the
		# value does not exist, while request.POST['<variable>']
		# will raise a KeyError exception.
		username = request.POST.get('username')
		password = request.POST.get('password')
		# Use Django's machinery to attempt to see if the username/password
		# combination is valid - a User object is returned if it is.
		user = authenticate(username=username, password=password)
		# If we have a User object, the details are correct.
		# If None (Python's way of representing the absence of a value), no user
		# with matching credentials was found.
		if user:
			# Is the account active? It could have been disabled.
			if user.is_active:
				# If the account is valid and active, we can log the user in.
				# We'll send the user back to the homepage.
				login(request, user)
				return redirect(reverse('explore_scotland_app:index'))
			else:
				# An inactive account was used - no logging in!
				return HttpResponse("Your Explore Scotland account is disabled.")
		else:
			# Bad login details were provided. So we can't log the user in.
			print(f"Invalid login details: {username}, {password}")
			return HttpResponse("Invalid login details supplied.")
	# The request is not a HTTP POST, so display the login form.
	# This scenario would most likely be a HTTP GET.
	else:
		# No context variables to pass to the template system, hence the
		# blank dictionary object...
		return render(request, 'explore_scotland_app/login.html')


def user_logout(request):
	# Since we know the user is logged in, we can now just log them out.
	logout(request)
	# Take the user back to the homepage.
	return redirect(reverse('explore_scotland_app:index'))

@login_required
def edit_profile(request):
	# If the request is a HTTP POST, try to pull out the relevant information.
	if request.method == 'POST':
		user_form = UserFormWithoutPassword(request.POST, instance = request.user)
		profile_form = UserProfileForm(request.POST, request.FILES, instance = request.user.profile)

		# If the two forms are valid...
		if user_form.is_valid() and profile_form.is_valid():
			# Save the user's form data to the database.
			user = user_form.save()

			# Now sort out the UserProfile instance.
			# Since we need to set the user attribute ourselves,
			# we set commit=False. This delays saving the model
			# until we're ready to avoid integrity problems.
			profile = profile_form.save(commit=False)
			profile.user = user

			# Did the user provide a profile picture?
			# If so, we need to get it from the input form and
			#put it in the UserProfile model.
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			# Now we save the UserProfile model instance.
			profile.save()

			# Update our variable to indicate that the template
			# registration was successful.
			ctx = {
				'changed': True,
			}
			return render(request, 'explore_scotland_app/edit-profile.html', ctx)
			
	user_form = UserFormWithoutPassword(instance = request.user)
	profile_form = UserProfileForm(instance = request.user.profile)
	ctx = {
		'user_form': user_form,
		'profile_form': profile_form
	}
	return render(request, 'explore_scotland_app/edit-profile.html', ctx)
	
def delete_user(request):
	try:
		request.user.delete()
	except:
		return HttpResponse("Unable to delete account.")
	return redirect(reverse('explore_scotland_app:index'))
	
@login_required
def upload_photo(request):
	# If the request is a HTTP POST, try to pull out the relevant information.
	if request.method == 'POST':
		photo_form = PhotoForm(request.POST, request.FILES)

		# If the form is valid...
		if photo_form.is_valid():

			photo = photo_form.save(commit=False)
			photo.owner = request.user.profile

			photo.save()

			# Update our variable to indicate that the template
			# registration was successful.
			ctx = {
				'successful': True,
			}
			return render(request, 'explore_scotland_app/upload-photo.html', ctx)
			
	photo_form = PhotoForm()
	ctx = {
		'photo_form': photo_form,
	}
	return render(request, 'explore_scotland_app/upload-photo.html', ctx)
	
@login_required
def delete_photo(request, photo_id):
	try:
		photo = Photo.objects.get(pk=photo_id)
	except Photo.DoesNotExist:
		return HttpResponse('Photo does not exist.')
	
	if photo.owner == request.user.profile:
		photo.delete()
	else:
		return HttpResponse('You are not the owner of this photo.')
	
	try:
		return redirect(request.META.get('HTTP_REFERER'))
	except:
		pass
	return redirect(reverse('explore_scotland_app:index'))
	
from django.core.serializers import serialize

@login_required
def get_photos(request):
	photos = serialize('json', Photo.objects.all()[:10])
	return JsonResponse(photos, safe=False)
	
@login_required
def get_liked_photos(request):
	photos = serialize('json', request.user.profile.photos_liked.all())
	return JsonResponse(photos, safe=False)
	
def picture_details(request, photo_id):
	try:
		photo = Photo.objects.get(pk=photo_id)
	except Photo.DoesNotExist:
		return HttpResponse('Photo does not exist.')
	
	comment_form = CommentForm()
	
	comments = photo.photo_comments.all()
	
	ctx = {
		'comment_form': comment_form,
		'photo': photo,
		'comments': comments
	}
	return render(request, 'explore_scotland_app/picture-details.html', ctx)
	
@login_required
def post_comment(request, photo_id):
	if request.method == 'POST':
		comment_form = CommentForm(request.POST)
		photo_id = comment_form.data.get('photo_id', None)
		comment_id = comment_form.data.get('comment_id', None)
		
		if comment_form.is_valid():
			comment = comment_form.save(commit=False)
			
			comment.owner = request.user.profile
			
			if comment_id:
				comment.comment = Comment.objects.get(pk=comment_id)
			elif photo_id:
				comment.photo = Photo.objects.get(pk=photo_id)
			
			comment.save()
			
			return redirect(reverse('explore_scotland_app:picture_details', kwargs={'photo_id':photo_id,}))
		else:
			return HttpResponse('Failed to add comment.')
	try:
		return redirect(request.META.get('HTTP_REFERER'))
	except:
		pass
	return redirect(reverse('explore_scotland_app:index'))
	
@login_required
def like_photo(request, photo_id):
	photo = Photo.objects.get(pk=photo_id)
	
	if request.user.profile in photo.likes.all():
		photo.likes.remove(request.user.profile)
	else:
		photo.likes.add(request.user.profile)
	
	try:
		return redirect(request.META['HTTP_REFERER'])
	except:
		pass
	return redirect(reverse('explore_scotland_app:index'))

def edit_photo(request, photo_id):
	photo = Photo.objects.get(pk=photo_id)
	if request.method == 'POST':
		photo_form = PhotoFormWithoutPhoto(request.POST, instance=photo)
	
		if photo_form.is_valid():
			photo_form.save()
		
			return redirect(reverse('explore_scotland_app:picture_details', kwargs={'photo_id':photo_id,}))
		else:
			return HttpResponse('Failed to edit photo.')
	photo_form = PhotoFormWithoutPhoto(instance=photo)
	ctx = {
		'photo_form': photo_form,
		'photo': photo
	}
	return render(request, 'explore_scotland_app/edit-photo.html', ctx)

def daily_board(request):
	return render(request, 'explore_scotland_app/daily-board.html')








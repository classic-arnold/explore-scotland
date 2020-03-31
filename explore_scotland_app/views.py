from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from explore_scotland_app.forms import UserForm, UserProfileForm, UserFormWithoutPassword, PhotoForm, CommentForm, PhotoFormWithoutPhoto
from explore_scotland_app.models import UserProfile, Photo, Comment
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

from django.core.serializers import serialize
import datetime

from django.db.models import Count, Q
import re

from django.contrib import messages

def pop_url(request_meta):
	try:
		return redirect(request_meta.get('HTTP_REFERER'))
	except:
		pass

# render the homepage (index.html)
def index(request):
	return render(request, 'explore_scotland_app/index.html')

# render the homepage (index.html)
def register(request):
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
			
			login(request, user, backend='django.contrib.auth.backends.ModelBackend')
			
			return redirect('explore_scotland_app:index')
	else:
		# Not a HTTP POST, so we render our form using two ModelForm instances.
		# These forms will be blank, ready for user input.
		user_form = UserForm()
		profile_form = UserProfileForm()

	# Render the template depending on the context.
	return render(request,'explore_scotland_app/register.html',context = {'user_form': user_form, 'profile_form': profile_form})

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
				messages.info(request, 'Your Explore Scotland account is disabled.')
				pop_url(request.META)
				return redirect(reverse('explore_scotland_app:login'))
		else:
			# Bad login details were provided. So we can't log the user in.
			messages.info(request, 'Invalid login details supplied.')
			pop_url(request.META)
			return redirect(reverse('explore_scotland_app:login'))
	# The request is not a HTTP POST, so display the login form.
	# This scenario would most likely be a HTTP GET.
	else:
		# No context variables to pass to the template system, hence the
		# blank dictionary object...
		return render(request, 'explore_scotland_app/login.html')

@login_required
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
			messages.info(request, 'Update successful.')
			return redirect(reverse('explore_scotland_app:index'))
			
	user_form = UserFormWithoutPassword(instance = request.user)
	profile_form = UserProfileForm(instance = request.user.profile)
	ctx = {
		'user_form': user_form,
		'profile_form': profile_form
	}
	return render(request, 'explore_scotland_app/edit-profile.html', ctx)

# delete a user
@login_required
def delete_user(request):
	# check if teh user exists first
	try:
		request.user.delete()
	except:
		messages.info(request, 'Unable to delete account.')
		pop_url(request.META)
		return redirect(reverse('explore_scotland_app:index'))

	# return to the homepage, if deletion succeeds or fails
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
			return redirect(reverse('explore_scotland_app:profile'))
			
	photo_form = PhotoForm()
	ctx = {
		'photo_form': photo_form,
	}
	return render(request, 'explore_scotland_app/upload-photo.html', ctx)

# delete a photo
@login_required
def delete_photo(request, photo_id):
	# check if the photo exists first
	try:
		photo = Photo.objects.get(pk=photo_id)
	except Photo.DoesNotExist:
		messages.info(request, 'You tried to delete a photo that does not exist.')
		pop_url(request.META)
		return redirect(reverse('explore_scotland_app:profile'))
	# check if the photois from the logged in user
	if photo.owner == request.user.profile:
		photo.delete()
	else:
		messages.info(request, 'You tried to delete a photo you do not own.')
		pop_url(request.META)
		return redirect(reverse('explore_scotland_app:profile'))
	# return to the account profile page
	return redirect(reverse('explore_scotland_app:profile'))
# get all photos
def get_all_photos(request, count):
	photos = serialize('json', Photo.objects.all().annotate(q_count=Count('likes')).order_by('-q_count')[:count])
	return JsonResponse(photos, safe=False)

# get photos from a time period past
def get_photos_from_days_ago(request, days):
	time = datetime.datetime.now() - datetime.timedelta(days = days)
	photos = serialize('json', Photo.objects.filter(date_added__gte=time).annotate(q_count=Count('likes')).order_by('-q_count')[:10])
	return JsonResponse(photos, safe=False)

# Search for a photo
def search_photos(request):
	if request.method == 'GET':
		# Get the search parameters for teh photo
		query_string = request.GET.get("keyword", '')
		sorted_by = request.GET.get("sort-by", '')
		category = request.GET.get("category", '')
		photos = None
		# ignore case-sensitivity
		words = re.split(r"[^A-Za-z']+", query_string)
		# send query
		query = Q()
		# analyze the search results
		for word in words:
    		# 'or' the queries together
   			query |= Q(description__icontains=word) | Q(tags__icontains=word)

		# check how the photos are sorted, by likes or time
		if sorted_by == 'likes':
			photos = Photo.objects.filter(query).annotate(q_count=Count('likes')).order_by('-q_count')
		elif sorted_by == 'latest':
			photos = Photo.objects.filter(query).order_by('-date_added')
		else:
			photos = Photo.objects.filter(query)
			
		if category != 'all':
			photos = photos.filter(categories=category)
		
		ctx = {
			'photos': photos,
			'query': query_string,
			'sorted_by': sorted_by,
			'category_searched': category
		}
		# show the search results
		return render(request, 'explore_scotland_app/search-photos.html', ctx)

# get the photo details
def picture_details(request, photo_id):
	# check first if the photo exists
	try:
		photo = Photo.objects.get(pk=photo_id)
	except Photo.DoesNotExist:
		messages.info(request, 'The photo you are looking for does not exist.')
		pop_url(request.META)
		return redirect(reverse('explore_scotland_app:index'))
	# get the comments for the photo
	comment_form = CommentForm()
	comments = photo.photo_comments.all()
	
	ctx = {
		'comment_form': comment_form,
		'photo': photo,
		'comments': comments
	}
	# show the photo details with comments
	return render(request, 'explore_scotland_app/picture-details.html', ctx)

# Add a comment to a photo
@login_required
def post_comment(request, photo_id):
	if request.method == 'POST':
		# The the photo details and the comment form
		comment_form = CommentForm(request.POST)
		photo_id = comment_form.data.get('photo_id', None)
		comment_id = comment_form.data.get('comment_id', None)

		# check if teh form is valid
		if comment_form.is_valid():
			comment = comment_form.save(commit=False)
			comment.owner = request.user.profile
			# check if comment or photo
			if comment_id:
				comment.comment = Comment.objects.get(pk=comment_id)
			elif photo_id:
				comment.photo = Photo.objects.get(pk=photo_id)
			# save the comment
			comment.save()
			
			return redirect(reverse('explore_scotland_app:picture_details', kwargs={'photo_id':photo_id,}))
		else:
			messages.info(request, 'Failed to add comment.')
			pop_url(request.META)
			return redirect(reverse('explore_scotland_app:picture_details', kwargs={'photo_id':photo_id,}))
	# update the information
	pop_url(request.META)
	return redirect(reverse('explore_scotland_app:picture_details', kwargs={'photo_id':photo_id,}))

# Like the photo
@login_required
def like_photo(request, photo_id):
	# get the photo id
	photo = Photo.objects.get(pk=photo_id)
	# Check if 'like all' is selected
	if request.user.profile in photo.likes.all():
		photo.likes.remove(request.user.profile)
	else:
		photo.likes.add(request.user.profile)
	# update the information
	pop_url(request.META)
	return redirect(reverse('explore_scotland_app:picture_details', kwargs={'photo_id':photo_id,}))

# Edit a photo
@login_required
def edit_photo(request, photo_id):
	# get the photo id
	photo = Photo.objects.get(pk=photo_id)
	# check if this is a valid photo
	if request.method == 'POST':
		photo_form = PhotoFormWithoutPhoto(request.POST, instance=photo)
		if photo_form.is_valid():
			photo_form.save()
			return redirect(reverse('explore_scotland_app:picture_details', kwargs={'photo_id':photo_id,}))
		else:
			messages.info(request, 'Failed to edit photo.')
			pop_url(request.META)
			return redirect(reverse('explore_scotland_app:picture_details', kwargs={'photo_id':photo_id,}))
	# load the phot details
	photo_form = PhotoFormWithoutPhoto(instance=photo)
	ctx = {
		'photo_form': photo_form,
		'photo': photo
	}
	# edit the requested photo
	return render(request, 'explore_scotland_app/edit-photo.html', ctx)

# request the profile page, a user must be logged in
def photo_board(request, board_type):
	# get the board type (daily, weekly, monthly or overall)
	ctx = {
		'board_type': board_type,
	}
	return render(request, 'explore_scotland_app/photo-board.html', ctx)

# request the profile page, a user must be logged in
@login_required
def profile(request):
	return render(request, 'explore_scotland_app/profile.html')

# request the about page
def about(request):
	return render(request, 'explore_scotland_app/about.html')







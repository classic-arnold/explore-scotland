from django.contrib import admin
from .models import UserProfile, Photo, Comment

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Photo)
admin.site.register(Comment)
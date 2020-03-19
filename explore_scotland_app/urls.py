from django.urls import path
from explore_scotland_app import views

app_name = 'explore_scotland_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('delete-account/', views.delete_user, name='delete_user'),
    path('upload-photo/', views.upload_photo, name='upload_photo'),
    path('delete-photo/<int:photo_id>', views.delete_photo, name='delete_photo'),
    path('get-all-photos/<int:count>', views.get_all_photos, name='get_all_photos'),
    path('get-photos-from-days-ago/<int:days>', views.get_photos_from_days_ago, name='get_photos_from_days_ago'),
    path('search-photos/', views.search_photos, name='search_photos'),
    path('get-liked-photos/', views.get_liked_photos, name='get_liked_photos'),
    path('picture-page/<int:photo_id>', views.picture_details, name='picture_details'),
    path('picture-page/', views.picture_details, name='picture_details_without_key'),
    path('post-comment/<int:photo_id>', views.post_comment, name='post_comment'),
    path('like-photo/<int:photo_id>', views.like_photo, name='like_photo'),
    path('edit-photo/<int:photo_id>', views.edit_photo, name='edit_photo'),
    path('photo-board/', views.photo_board, {'board_type': 'overall-board'}, name='photo_board'),
    path('photo-board/<slug:board_type>', views.photo_board, name='photo_board'),
    path('profile', views.profile, name='profile'),
    
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
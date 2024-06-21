from django.urls import path
from . import views
from .views import SearchResultsView

urlpatterns = [
    path('', views.user_login, name='user_login'),
    path('register/', views.register, name='register'),
    path('user_login/', views.user_login, name='user_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('user_logout/', views.user_logout, name='user_logout'),

    path('upload/gallery/', views.upload_gallery, name='upload_gallery'),
    path('upload/video/', views.upload_video, name='upload_video'),
    path('add/location/', views.add_location, name='add_location'),
    path('create/post/', views.create_post, name='create_post'),

    path('profile', views.profile, name='profile'),
    path('profile_update/<int:user_id>/', views.profile_update, name='profile_update'),

    path("search/", SearchResultsView.as_view(), name="search_results"),

    path('send_friend_request/<str:to_username>/', views.send_friend_request, name='send_friend_request'),

    path('friend_requests_view', views.friend_requests_view, name='friend_requests_view'),
    path('accept-friend-request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),

    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('get_comments/<int:post_id>/', views.get_comments, name='get_comments'),

    path('video/<int:id>/', views.video, name='video'),

    path('friends/<int:id>/', views.friends, name='friends'),
    path('send_message/', views.send_message, name='send_message'),
]

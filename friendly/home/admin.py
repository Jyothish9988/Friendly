from django.contrib import admin
from .models import Post, UserProfile, FriendRequest,Chat

admin.site.register(UserProfile)
admin.site.register(Post)
admin.site.register(FriendRequest)
admin.site.register(Chat)


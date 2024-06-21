from django.contrib import admin
from .models import Post, UserProfile, FriendRequest,Message,Like,Comment

admin.site.register(UserProfile)
admin.site.register(Post)
admin.site.register(FriendRequest)
admin.site.register(Message)
admin.site.register(Like)
admin.site.register(Comment)


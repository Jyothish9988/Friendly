from django.contrib.auth.models import User
from django.db import models


class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    admin_reply = models.TextField(blank=True)


class Post(models.Model):
    FILE_TYPE_CHOICES = (
        ('post', 'Post'),
        ('location', 'Location'),
        ('gallery', 'Gallery'),
        ('video', 'Video'),
    )
    FOR_KIDS = (
        ('new', 'new'),
        ('yes', 'Yes'),
        ('no', 'No'),

    )

    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_picture = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    video = models.FileField(upload_to='videos/', null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default='')
    lim = models.CharField(max_length=20, choices=FOR_KIDS, default='new')
    report = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.title

    def get_uploaded_by_profile_picture(self):
        return self.uploaded_by.userprofile.profile_picture.url if self.uploaded_by.userprofile.profile_picture else None


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    username = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.username.username


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_requests_sent')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_requests_received')
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"From: {self.from_user.username}, To: {self.to_user.username}, Accepted: {self.is_accepted}"


class Chat(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='chat/images/', blank=True, null=True)
    receiver_image = models.ImageField(upload_to='chat/images/', blank=True, null=True)
    file = models.FileField(upload_to='chat/files/', blank=True, null=True)
    video = models.FileField(upload_to='chat/videos/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} to {self.receiver} at {self.timestamp}"

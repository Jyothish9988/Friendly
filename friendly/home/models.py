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

    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    video = models.FileField(upload_to='videos/', null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default='')

    def __str__(self):
        return self.title

from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms.widgets import PasswordInput, TextInput
from django import forms
from .models import Post, UserProfile, Comment
from django.core.exceptions import ValidationError


class CreateUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists")
        return username


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=PasswordInput())


class GalleryUploadForm(forms.Form):
    gallery_title = forms.CharField(max_length=100)
    gallery_description = forms.CharField(widget=forms.Textarea)
    gallery_file = forms.FileField()


class VideoUploadForm(forms.Form):
    video_title = forms.CharField(max_length=100)
    video_description = forms.CharField(widget=forms.Textarea)
    video_file = forms.FileField()


class LocationForm(forms.Form):
    location_name = forms.CharField(max_length=100)
    gps_coordinates = forms.CharField(max_length=100, required=False)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'is_public', 'video', 'image', 'location']


class ProfileUpdate(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio', 'gender', 'date_of_birth', 'phone_number']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

from django.views.generic import TemplateView, ListView
from .forms import CreateUserForm, LoginForm
from django.contrib.auth import authenticate, login as auth_login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import GalleryUploadForm, VideoUploadForm, LocationForm, PostForm
from django.contrib import messages
from .models import Post, UserProfile,FriendRequest
from django.db.models import Q


def register(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(username=user)
            return redirect("user_login")
    else:
        form = CreateUserForm()

    context = {'registerform': form}
    return render(request, 'register.html', context=context)


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                if user.is_staff:
                    return redirect("admin:index")
                else:
                    return redirect('dashboard')
    else:
        form = LoginForm()

    context = {'loginform': form}
    return render(request, 'login.html', context=context)


@login_required(login_url='/user_login')
def user_logout(request):
    logout(request)
    return redirect('user_login')


@login_required(login_url='/user_login')
def dashboard(request):
    user = request.user
    profile = get_object_or_404(UserProfile, username=user)
    users = UserProfile.objects.exclude(username=user)

    if not profile.full_name or not profile.phone_number:
        messages.error(request, 'Please update your profile details.')

    posts = Post.objects.filter(is_public=True).order_by('-uploaded_at')

    return render(request, 'dashboard.html', {
        'profile': profile,
        'messages': messages.get_messages(request),
        'posts': posts,

    })


class SearchResultsView(ListView):
    model = UserProfile
    template_name = "search_result.html"

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            return UserProfile.objects.filter(
                Q(username__username__icontains=query) | Q(full_name__icontains=query)
            )
        return UserProfile.objects.none()


@login_required(login_url='/user_login')
def profile(request):
    user = request.user
    user_profile = request.user
    profile = get_object_or_404(UserProfile, username=user.id)
    details = UserProfile.objects.filter(username=user)

    if not profile.full_name or not profile.phone_number:
        messages.error(request, 'Please update your profile details.')
    posts = Post.objects.filter(is_public=True).order_by('-uploaded_at')

    return render(request, 'profile.html', {
        'profile': profile,
        'messages': messages.get_messages(request),
        'posts': posts,
        'details': details,
        'user_profile': user_profile,
    })


@login_required(login_url='/user_login')
def upload_gallery(request):
    if request.method == 'POST':
        form = GalleryUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Extract form data
            gallery_title = form.cleaned_data['gallery_title']
            gallery_description = form.cleaned_data['gallery_description']
            gallery_file = form.cleaned_data['gallery_file']

            # Create Post object
            post = Post.objects.create(
                uploaded_by=request.user,
                title=gallery_title,
                description=gallery_description,
                image=gallery_file,
                file_type='gallery'
            )
            messages.success(request, 'Gallery uploaded successfully.')
            return redirect('dashboard')
    else:
        form = GalleryUploadForm()
    return render(request, 'upload_gallery.html', {'form': form})


@login_required(login_url='/user_login')
def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Extract form data
            video_title = form.cleaned_data['video_title']
            video_description = form.cleaned_data['video_description']
            video_file = form.cleaned_data['video_file']

            # Create Post object
            post = Post.objects.create(
                uploaded_by=request.user,
                title=video_title,
                description=video_description,
                video=video_file,
                file_type='video'
            )
            messages.success(request, 'Video uploaded successfully.')
            return redirect('dashboard')
    else:
        form = VideoUploadForm()
    return render(request, 'upload_video.html', {'form': form})


@login_required(login_url='/user_login')
def add_location(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            # Extract form data
            location_name = form.cleaned_data['location_name']
            gps_coordinates = form.cleaned_data['gps_coordinates']

            # Create Post object
            post = Post.objects.create(
                uploaded_by=request.user,
                title=location_name,
                location=gps_coordinates,
                file_type='location'
            )
            messages.success(request, 'Location added successfully.')
            return redirect('dashboard')
    else:
        form = LocationForm()
    return render(request, 'add_location.html', {'form': form})


@login_required(login_url='/user_login')
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            # Save form data to Post model
            post = form.save(commit=False)
            post.uploaded_by = request.user
            post.file_type = 'post'
            post.save()
            messages.success(request, 'Post created successfully.')
            return redirect('dashboard')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})


@login_required
def profile_update(request, user_id):
    user_instance = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserProfile, username=user_instance)

    if request.method == 'POST':
        profile.full_name = request.POST.get('full_name')
        profile.bio = request.POST.get('bio')
        profile.gender = request.POST.get('gender')
        profile.date_of_birth = request.POST.get('date_of_birth')
        profile.email = request.POST.get('email')
        profile.phone_number = request.POST.get('phone_number')
        profile.save()
        messages.success(request, 'Profile updated successfully!')

        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'profile.html', {
        'profile': profile,
    })


# -----------------------------------friend req start------------------------
@login_required
def send_friend_request(request, to_username):
    if request.method == 'POST':
        # Get the user object by username
        receiver_user = get_object_or_404(User, username=to_username)
        existing_request = FriendRequest.objects.filter(from_user=request.user, to_user=receiver_user).exists()
        if not existing_request and request.user != receiver_user:
            FriendRequest.objects.create(from_user=request.user, to_user=receiver_user)
    return redirect('dashboard')


@login_required
def friend_requests_view(request):
    logged_in_username = request.user.username
    friend_requests = FriendRequest.objects.filter(to_user__username=logged_in_username)

    friend_requests_with_profiles = []
    for fr in friend_requests:
        try:
            to_user_profile = UserProfile.objects.get(username=fr.to_user)
            friend_requests_with_profiles.append({
                'id': fr.id,  # Ensure the ID is included
                'from_user': fr.from_user,
                'to_user': fr.to_user,
                'is_accepted': fr.is_accepted,
                'created_at': fr.created_at,
                'to_user_profile': to_user_profile
            })
        except UserProfile.DoesNotExist:
            friend_requests_with_profiles.append({
                'id': fr.id,  # Ensure the ID is included
                'from_user': fr.from_user,
                'to_user': fr.to_user,
                'is_accepted': fr.is_accepted,
                'created_at': fr.created_at,
                'to_user_profile': None
            })

    return render(request, 'request.html', {'friend_requests_with_profiles': friend_requests_with_profiles})


@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)

    if friend_request.is_accepted:
        return redirect('friend_requests')

    friend_request.is_accepted = True
    friend_request.save()

    return redirect('friend_requests')
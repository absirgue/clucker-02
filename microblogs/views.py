"""Views of the microblogs app."""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from .forms import LogInForm, PostForm, SignUpForm
from .models import Post, User
from django.conf import settings


def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
            # execute
    return modified_view_function


@login_required
def feed(request):
    def post_created_at(post):
        return post.created_at
    form = PostForm()
    posts = Post.objects.filter(author=request.user)
    authors = list(request.user.followees.all()) + [request.user]
    posts = Post.objects.filter(author__in=authors)
    # NOTE: we can remove next line, it is just for learning purposes (for later projects)
    posts.sort(key=post_created_at, reverse=True)
    return render(request, 'feed.html', {'form': form, 'user': request.user, 'posts': posts})


@login_prohibited
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                redirect_url = request.POST.get('next') or 'feed'
                return redirect(redirect_url)
        messages.add_message(request, messages.ERROR,
                             "The credentials provided were invalid!")
    form = LogInForm()
    next = request.GET.get('next') or ''
    return render(request, 'log_in.html', {'form': form, 'next': next})


def log_out(request):
    logout(request)
    return redirect('home')


@login_prohibited
def home(request):
    return render(request, 'home.html')


@login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})


@login_required
def show_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        posts = Post.objects.filter(author=user)
        following = request.user.is_following(user)
        if user_id == request.user.id:
            followable = False
        else:
            followable = True
    except ObjectDoesNotExist:
        return redirect('user_list')
    else:
        return render(request, 'show_user.html', {'user': user, 'posts': posts, 'following': following, 'followable': followable})


@login_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})


def new_post(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            current_user = request.user
            form = PostForm(request.POST)
            if form.is_valid():
                text = form.cleaned_data.get('text')
                post = Post.objects.create(author=current_user, text=text)
                return redirect('feed')
            else:
                return render(request, 'feed.html', {'form': form})
        else:
            return redirect('log_in')
    else:
        return HttpResponseForbidden()


@login_required
def follow_toggle(request, user_id):
    current_user = request.user
    try:
        followee = User.objects.get(id=user_id)
        current_user.toggle_follow(followee)
    except ObjectDoesNotExist:
        return redirect('user_list')
    else:
        return redirect('show_user', user_id=user_id)

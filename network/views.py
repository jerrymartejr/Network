from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, Following, Like


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    liked_posts = []

    user = request.user

    if user.is_authenticated:
        liked = Like.objects.filter(user=user)
        
        for like in liked:
            liked_posts.append(like.post)

    return render(request, "network/index.html", {
        "page_obj": page_obj,
        "liked_posts": liked_posts
    })


# New Post
def new_post(request):
    if request.method == "POST":
        body = request.POST["new_post"]
        user = request.user

        post = Post(body=body, user=user)
        post.save()
        return HttpResponseRedirect(reverse("index"))


# Profile Page
def profile(request, user_id):
    profile_user = User.objects.filter(pk=user_id).first()

    followers = Following.objects.filter(followed=profile_user)
    num_followers = followers.count()

    following = Following.objects.filter(follower=profile_user)
    num_following = following.count()

    followed = False

    for foll in followers:
        if foll.follower == request.user:
            followed = True

    posts = Post.objects.filter(user=profile_user)
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    user = request.user
    liked = Like.objects.filter(user=user)

    user_likes = list(user.likes.all())

    liked_posts = []
    for like in liked:
        liked_posts.append(like.post)

    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "num_followers": num_followers,
        "num_following": num_following,
        "followed": followed,
        "page_obj": page_obj,
        "followers": followers,
        "liked_posts": liked_posts
    })


def follow(request):
    if request.method == "POST":
        user_id = request.POST["user_id"]
        followed = User.objects.get(pk=user_id)
        follower = request.user

        follow = Following(follower=follower, followed=followed)
        follow.save()
        return HttpResponseRedirect(reverse("profile", args=(user_id)))


def unfollow(request):
    if request.method == "POST":
        user_id = request.POST["user_id"]
        followed = User.objects.get(pk=user_id)
        follower = request.user

        follow = Following.objects.filter(follower=follower, followed=followed).first()
        follow.delete()
        return HttpResponseRedirect(reverse("profile", args=(user_id)))


# Following
@login_required
def following(request):

    # list of users that the current user is following
    followed_users = []

    following = Following.objects.filter(follower=request.user)

    for follow in following:
        followed_users.append(follow.followed)

    posts = Post.objects.filter(user__in=followed_users)
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    

    return render(request, "network/following.html", {
        "page_obj": page_obj,
        "following": following
    })


# Edit Post if not using JavaScript
# def edit_post(request):
    # if request.method == "POST":
        # user_id = request.POST["user_id"]

        # post_id = request.POST["post_id"]
        # post = Post.objects.get(pk=post_id)

        # body = request.POST["edited_post"]
        # post.body = body
        # post.save()
        # return HttpResponseRedirect(reverse("profile", args=(user_id)))


# Edit Post
@csrf_exempt
@login_required
def edit_post(request):
    if request.method == "POST":
        data = json.loads(request.body)

        post_id = data.get("post_id", "")
        body = data.get("body", "")

        post = Post.objects.get(pk=post_id)
        post.body = body
        post.save()

        return JsonResponse({"message": "Post edited successfully.","body": body}, status=201)


# "Like" and "Unlike"
@csrf_exempt
@login_required
def like(request):
    if request.method == "POST":
        data = json.loads(request.body)

        post_id = data.get("post_id", "")

        post = Post.objects.get(pk=post_id)
        user = request.user

        like = Like(user=user, post=post)
        like.save()

        num_likes = post.likes.count()

        return JsonResponse({"message": "Liked post.", "num_likes": num_likes}, status=201)


@csrf_exempt
@login_required
def unlike(request):
    if request.method == "POST":
        data = json.loads(request.body)

        post_id = data.get("post_id", "")

        post = Post.objects.get(pk=post_id)
        user = request.user

        like = Like.objects.filter(post=post, user=user).first()
        like.delete()

        num_likes = post.likes.count()

        return JsonResponse({"message": "Unliked post.", "num_likes": num_likes}, status=201)



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

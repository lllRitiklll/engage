from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Post, Like, Comment
from users.models import Notification, User
from django.shortcuts import get_object_or_404



@login_required
def feed(request):
    posts = Post.objects.all().order_by('-created_at')

    liked_posts = []
    unread_count = 0
    users = User.objects.exclude(id=request.user.id)

    if request.user.is_authenticated:
        liked_posts = Like.objects.filter(
            user=request.user
        ).values_list('post_id', flat=True)

        unread_count = Notification.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()

    return render(request, 'feed.html', {
        'posts': posts,
        'liked_posts': liked_posts,
        'unread_count': unread_count,
        'users': users
    })



@login_required
def like_post(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    post = get_object_or_404(Post, id=post_id)
    user = request.user

    like = Like.objects.filter(user=user, post=post)
    liked = False

    if like.exists():
        like.delete()
    else:
        Like.objects.create(user=user, post=post)
        liked = True

        if post.user != user:
            Notification.objects.create(
                sender=user,
                receiver=post.user,
                message="liked your post"
            )

    return JsonResponse({
        'liked': liked,
        'likes_count': post.like_set.count()
    })
    post = Post.objects.get(id=post_id)
    user = request.user

    like = Like.objects.filter(user=user, post=post)
    liked = False

    if like.exists():
        like.delete()
    else:
        Like.objects.create(user=user, post=post)
        liked = True

        # 🔔 notification
        if post.user != user:
            Notification.objects.create(
                sender=user,
                receiver=post.user,
                message="liked your post"
            )

    return JsonResponse({
        'liked': liked,
        'likes_count': post.like_set.count()
    })


@login_required
def add_comment(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(id=post_id)
        user = request.user
        text = request.POST.get('text')

        comment = Comment.objects.create(
            user=user,
            post=post,
            text=text
        )

        # 🔔 notification
        if post.user != user:
            Notification.objects.create(
                sender=user,
                receiver=post.user,
                message="commented on your post"
            )

        return JsonResponse({
            'username': user.username,
            'text': comment.text
        })


@login_required
def create_post(request):
    if request.method == "POST":
        image = request.FILES.get('image')
        caption = request.POST.get('caption')

        if image:
            Post.objects.create(
                user=request.user,
                image=image,
                caption=caption
            )
            return redirect('feed')

    return render(request, 'create_post.html')

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.user == request.user:
        post.delete()

    return redirect('feed')

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.user != request.user:
        return redirect('feed')

    if request.method == "POST":
        caption = request.POST.get('caption')
        image = request.FILES.get('image')

        post.caption = caption

        if image:
            post.image = image

        post.save()
        return redirect('feed')

    return render(request, 'edit_post.html', {'post': post})
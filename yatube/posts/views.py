from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Follow
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from .utils import get_page_context
from django.views.decorators.cache import cache_page


@cache_page(20, key_prefix="index_page")
def index(request):

    template = 'posts/index.html'
    post_list = Post.objects.all()
    context = get_page_context(post_list, request)
    return render(request, template, context)


# Страница с постами, отфильтрованными по группам
def group_posts(request, slug):
    template = 'posts/group_list.html',
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.order_by('-pub_date')
    context = {
        'group': group
    }
    context.update(get_page_context(post_list, request))
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    user = User.objects.get(username=username)
    post_list = (Post.objects.filter
                 (author=user))
    following = request.user.is_authenticated and (
        request.user.follower.filter(author=user).exists()
    )
    context = {
        'author': user,
        'following': following
    }
    context.update(get_page_context(post_list, request))
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    context = {
        'post': post,
        'form': CommentForm(request.POST or None),
        'switched_to_post_detail': True
    }
    return render(request, template, context)


@login_required
def post_create(request):

    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    template = 'posts/create_post.html'
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)

    return render(request, template,
                  {'form': form, 'username': request.user, 'is_edit': False})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    template = 'posts/create_post.html'
    if post.author != request.user:
        return redirect('posts:index')
    else:
        form = PostForm(request.POST or None,
                        files=request.FILES or None,
                        instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post.id)
        return render(request, template,
                      {'form': form, 'username': request.user,
                       'is_edit': True})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    template = 'posts/follow.html'
    context = {
        'follow': True
    }
    context.update(get_page_context(post_list, request))
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    follower = request.user
    following = get_object_or_404(User, username=username)
    if follower != following:
        Follow.objects.get_or_create(user=follower, author=following)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    follower = request.user
    following = get_object_or_404(User, username=username)
    follower.follower.filter(author=following).delete()
    return redirect('posts:profile', username=username)

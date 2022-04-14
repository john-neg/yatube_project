from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, Group, User
from .forms import PostForm, CommentForm
from .func import paginator


def index(request: HttpRequest) -> HttpResponse:
    template = 'posts/index.html'
    post_list = Post.objects.select_related('author', 'group').all()
    page_obj = paginator(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author').all()
    page_obj = paginator(post_list, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    post_list = user.posts.select_related('group').all()
    page_obj = paginator(post_list, request)
    context = {
        'user_data': user,
        'page_obj': page_obj,
        'following': True
    }
    return render(request, template, context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    template = 'posts/post_detail.html'
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        pk=post_id
    )
    form = CommentForm
    comments = post.comments.select_related('post').all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    return render(request, template, {'form': form})


@login_required
def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.id)
    return render(
        request,
        template,
        {'form': form, 'is_edit': True}
    )


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    # информация о текущем пользователе доступна в переменной request.user
    user = request.user
    context = {}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request: HttpRequest, username: str) -> HttpResponse:
    # Подписаться на автора
    pass


@login_required
def profile_unfollow(request: HttpRequest, username: str) -> HttpResponse:
    # Дизлайк, отписка
    pass

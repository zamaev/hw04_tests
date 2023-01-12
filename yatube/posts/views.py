from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.utils import get_page_obj

from .forms import PostForm, CommentForm
from .models import Group, Post, User


def index(request):
    page_obj = get_page_obj(request, Post.objects.all())

    return render(request, 'posts/index.html', {
        'page_obj': page_obj,
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    page_obj = get_page_obj(request, group.posts.all())

    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': page_obj,
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    page_obj = get_page_obj(request, author.posts.all())

    return render(request, 'posts/profile.html', {
        'author': author,
        'page_obj': page_obj,
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    return render(request, 'posts/post_detail.html', {
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.all(),
    })


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)

    return render(request, 'posts/create_post.html', {
        'form': form,
    })


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)

    return render(request, 'posts/create_post.html', {
        'form': form,
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)

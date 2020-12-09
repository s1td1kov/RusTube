from django import forms
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import (get_list_or_404, get_object_or_404, redirect,
                              render)
from django.views.decorators.cache import cache_page

from .contansts import POSTS_PER_PAGE
from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    form = PostForm(request.POST)
    if request.method == 'POST' and form.is_valid():
        new_form = form.save(commit=False)
        new_form.author = request.user
        new_form.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form, 'edit': False})


def profile(request, username):
    post_author = get_object_or_404(User, username=username)
    followings = Follow.objects.filter(author_id=post_author.id).count()
    followers = Follow.objects.filter(user_id=post_author.id).count()
    following = Follow.objects.filter(
        author_id=post_author.id, user_id=request.user.id)
    post_list = post_author.posts.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {
        'paginator': paginator,
        'page': page,
        'username': post_author,
        'following': following,
        'followings': followings,
        'followers': followers,
    })


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    followings = Follow.objects.filter(author_id=post.author.id).count()
    followers = Follow.objects.filter(user_id=post.author.id).count()
    post_count = post.author.posts.count()
    comments = post.comments.all()
    return render(request, 'post.html', {'post': post,
                                         'post_count': post_count,
                                         'username': post.author,
                                         'form': CommentForm(),
                                         'comments': comments,
                                         'followings': followings,
                                         'followers': followers,
                                         }
                  )


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    if post.author != request.user:
        return redirect('post', username=post.author, post_id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if not form.is_valid():
        return render(request, 'new.html', {
            'form': form,
            'post': post,
            'edit': True,
        })
    form.save()
    return redirect('post', username, post_id)


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.author_id = request.user.id
        new_comment.post_id = post_id
        new_comment.save()
    return redirect('post', username, post_id)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(
        author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'follow.html',
        {'page': page, 'paginator': paginator}
    )


@login_required
def profile_follow(request, username):
    if request.user.username != username and not Follow.objects.filter(user_id=request.user.id, author_id=User.objects.get(username=username).id).exists():
        Follow.objects.create(
            user_id=request.user.id, author_id=User.objects.get(username=username).id)
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    follow_del = Follow.objects.get(
        user_id=request.user.id, author_id=User.objects.get(username=username).id)
    follow_del.delete()
    return redirect('profile', username)

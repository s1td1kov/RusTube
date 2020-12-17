from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


@cache_page(20)
def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
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
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group,
                                          'page': page,
                                          'paginator': paginator})


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
    post_count = post_author.posts.count()
    followings = Follow.objects.filter(author_id=post_author.id).count()
    followers = Follow.objects.filter(user_id=post_author.id).count()
    following = Follow.objects.filter(
        author_id=post_author.id, user_id=request.user.id)
    posts = post_author.posts.all()
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {
        'post_count': post_count,
        'paginator': paginator,
        'page': page,
        'username': post_author,
        'is_following': following,
        'followings': followings,
        'followers': followers,
    })


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    followings = Follow.objects.filter(author_id=post.author.id).count()
    followers = Follow.objects.filter(user_id=post.author.id).count()
    following = Follow.objects.filter(
        author_id=post.author.id, user_id=request.user.id)
    post_count = post.author.posts.count()
    comments = post.comments.all()
    return render(request, 'post.html', {'post': post,
                                         'post_count': post_count,
                                         'username': post.author,
                                         'form': CommentForm(),
                                         'comments': comments,
                                         'followings': followings,
                                         'followers': followers,
                                         'is_following': following,
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
    form = CommentForm(request.POST or None)
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
    posts = Post.objects.filter(
        author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'follow.html',
        {'page': page, 'paginator': paginator}
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user_id=request.user.id,
            author_id=author.id,
        )
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user_id=request.user.id,
        author_id=User.objects.get(username=username).id).delete()
    return redirect('profile', username)

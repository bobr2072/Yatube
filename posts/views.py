from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import page_objects
from users.forms import CreationForm

from .forms import CommentForm, PostForm, GroupForm
from .models import Follow, Group, Post, User


def index(request):

    paginator = Paginator(Post.objects.all(), page_objects)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'posts/index.html', {'page_obj': page_obj})


def group_posts(request, slug):

    group = get_object_or_404(Group, slug=slug)
    posts = group.group_page.all()
    paginator = Paginator(posts, page_objects)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'title': f'Записи сообщества {group}',
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)



def profile(request, username):

    author = get_object_or_404(User, username=username)
    all_posts = Post.objects.all().filter(author__username=username)
    paginator = Paginator(all_posts, page_objects)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user,
                                          author__username=username).exists()
    context = {
        'page_obj': page_obj,
        'author': author,
        'paginator': paginator,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


@login_required
def profile_edit(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        return redirect('posts:profile',
                        username
                        )
    form = CreationForm(request.POST or None,
                        files=request.FILES or None,
                        instance=author)

    if form.is_valid():
        form.save()
        return redirect('posts:profile', username)
    context = {
        'form': form,
        'author': author,
    }
    return render(request, 'posts/profile_edit.html', context)


def post_detail(request, post_id):

    post = get_object_or_404(Post, id=post_id)
    author = get_object_or_404(User, username=post.author)
    all_posts = Post.objects.all().filter(author__username=post.author)
    form = CommentForm(request.POST)
    comments = post.comments.all()
    context = {
        'author': author,
        'post': post,
        'post_id': post_id,
        'all_posts': all_posts,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)

    return render(request, 'posts/post_create.html', {'form': form})


@login_required
def group_create(request):
    form = GroupForm(request.POST or None,
                    files=request.FILES or None)

    if form.is_valid():
        group = form.save(commit=False)
        group.save()
        return redirect('posts:index')

    return render(request, 'posts/group_create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = get_object_or_404(User, username=post.author)
    if request.user != post.author:
        return redirect('posts:post_detail',
                        post_id=post.id
                        )
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'author': author,
        'post': post,
        'post_id': post_id,
    }
    return render(request, 'posts/post_edit.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, page_objects)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'posts/follow.html', {'page_obj': page_obj, })


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=username)
    if request.user == user:
        return redirect('posts:profile', username)
    Follow.objects.get_or_create(user=request.user,
                                 author=user)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    request.user.follower.get(author__username=username).delete()
    return redirect('posts:profile', username)

@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail',
                        post_id=post.id
                        )
    post.delete()
    return redirect('posts:profile', post.author)


def server_error(request):
    return render(request, 'core/500.html', status=500)


def permission_denied(request):
    return render(request, 'core/403.html', status=403)

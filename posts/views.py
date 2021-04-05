from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from yatube import settings

from .forms import CommentForm, PostForm
from .models import Group, Post, Comment, Follow


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, settings.PAR_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {
            'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_list = Post.objects.filter(group=group).order_by('-pub_date')
    paginator = Paginator(group_list, settings.PAR_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if len(group_list) > 10:
        return render(request, 'group.html',
                      {'group': group, 'page': page,
                       'paginator': paginator})
    return render(request, 'group.html',
                  {'group': group, 'page': page})


@login_required
def post_new(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post_new = form.save(commit=False)
        post_new.author = request.user
        post_new.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    post = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=post).order_by('-pub_date')
    number_of_posts = user_posts.count()
    paginator = Paginator(user_posts, settings.PAR_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=post).exists()
    return render(request, 'profile.html',
                  {'author': post,
                   'post': post,
                   'page': page,
                   'number_of_posts': number_of_posts,
                   'following': following})


def post_view(request, username: str, post_id: int):
    """Возвращает страницу просмотра конкретного поста"""
    post = get_object_or_404(Post, id=post_id)
    number_of_posts = Post.objects.filter(author=post.author).select_related("author").count()
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post__id=post_id)
    context = {
        "author": post.author,
        "post": post,
        "number_of_posts": number_of_posts,
        "form": form,
        "comments": comments,
        "post_id": post_id
    }
    return render(request, "post.html", context)


@login_required
def post_edit(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
    if request.user != profile:
        return redirect('post', username=username, post_id=post_id)
    # добавим в form свойство files
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect("post", username=request.user.username, post_id=post_id)

    return render(
        request, 'new.html', {'form': form, 'post': post})


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию, 
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect("post", username, post_id)
    return render(request, "includes/comments.html", {"form": form, 'post': post})


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user).order_by('-pub_date')
    paginator = Paginator(posts, settings.PAR_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator
    }
    return render(request, 'follow.html', context)



@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user_id=request.user.id, author_id=author.id)
    return redirect("profile", username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.filter(user_id=request.user, author_id=author).delete()
    return redirect("profile", username)
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from .utils import paginator_page


def index(request):
    # Все записи
    return render(request, 'posts/index.html', {
        'page_obj': paginator_page(
            request, Post.objects.select_related('group').all()),
    })


def group_posts(request, slug):
    # Записи группы
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'page_obj': paginator_page(request, group.posts.all()),
        'group': group,
    })


def profile(request, username):
    # Профиль пользователя
    author = get_object_or_404(User, username=username)
    context = {
        'page_obj': paginator_page(request, author.posts.all()),
        'author': author
    }
    if not request.user.is_authenticated:
        return render(request, 'posts/profile.html', context)
    if Follow.objects.filter(
            user=request.user,
            author=author).exists():
        result = True
    else:
        result = False
    context['following'] = result
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    # Детали записи
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': post.comments.all(),
        'form': CommentForm(request.POST or None),
    })


@login_required
def post_create(request):
    # Создание записи
    form = PostForm(request.POST or None,
                    files=request.FILES or None,)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {
            'form': form,
        })
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    form.save_m2m()
    return redirect('posts:profile', username=post.author)


@login_required
def post_edit(request, post_id):
    # Редактирование записи
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {
            'form': form,
        })
    form.save()
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    # Создание комментраия
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
    # Посты избранных авторов
    post_list = Post.objects.filter(
        author__following__user=request.user)
    return render(request, 'posts/follow.html', {
        'page_obj': paginator_page(request, post_list)})


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    if author == request.user:
        return redirect('posts:profile', username=username)
    Follow.objects.get_or_create(
        user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author,).delete()
    return redirect('posts:profile', username=username)

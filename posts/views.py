from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page

@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)

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
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request,
                  "group.html",
                  {"group": group,
                   "page": page,
                   'paginator': paginator})


@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST or None, files=request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.count()
    paginator = Paginator(author.posts.all(), 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request,
                  'profile.html',
                  {'author': author,
                   'count': posts, "page": page,
                   'paginator': paginator})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    author = post.author
    count = author.posts.count()
    form = CommentForm()
    items = post.comments.all()
    return render(request,
                  'post.html', {'post': post, 'author': author, 'count': count,
                                'form': form, 'items': items})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if post.author == request.user:
        if request.method == "POST":
            form = PostForm(request.POST or None, files=request.FILES or None,
                            instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect('post', username=username, post_id=post.id)
        else:
            form = PostForm(instance=post)
        return render(request, 'new_post.html', {'form': form,
                                                 'is_created': True,
                                                 'post': post})
    return redirect('post', username=username, post_id=post.id)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, 'comments.html', {'form': form})

from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail

from blog.forms import EmailPostForm
from config.settings import EMAIL_HOST_USER
from .models import Post


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request,'blog/post/list.html', {'page': page, 'posts': posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', published_at__year=year,
                             published_at__month=month, published_at__day=day)
    return render(request,'blog/post/detail.html',{'post': post})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent= False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())

            subject = f'{cd["name"]} ({cd["email"]}) recommends you reading {post.title}'
            message = f'Read {post.title} at {post_url} \n\n {cd["name"]}\'s comments {cd["comments"]}'

            send_mail(subject, message, EMAIL_HOST_USER,
                      [cd['to']], fail_silently=False)
            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html',
        {'post': post, 'form': form, 'sent': sent})

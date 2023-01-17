from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin, CreateView
from django.views.generic import UpdateView
from django.views.generic.list import ListView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.conf import settings

from core.views import DetailListView
from .forms import PostForm, CommentForm
from .models import User, Group, Post


class IndexView(ListView):
    model = Post
    template_name = 'posts/index.html'
    paginate_by = settings.POSTS_PER_PAGE


class GroupView(DetailListView):
    template_name = 'posts/group_list.html'
    general_object_model = Group
    general_object_context_name = 'group'
    relate_objects_name = 'posts'


class ProfileView(DetailListView):
    template_name = 'posts/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    general_object_model = User
    general_object_context_name = 'author'
    relate_objects_name = 'posts'


class PostDetailView(FormMixin, DetailView):
    form_class = CommentForm
    model = Post
    slug_url_kwarg = 'post_id'
    slug_field = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.get_object().comments.all()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'posts/create_post.html'
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('posts:profile', args=(self.request.user,))


class PostEditView(LoginRequiredMixin, UpdateView):
    template_name = 'posts/create_post.html'
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect(self.get_object())
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('posts:post_detail', args=(self.get_object().pk,))


class AddCommentView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = CommentForm
    pk_url_kwarg = 'post_id'

    def get(self, request, *args, **kwargs):
        return redirect(self.get_object())

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.get_object()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('posts:post_detail', args=(self.get_object().pk,))

from django.views.generic.base import TemplateView
from django.urls import path

app_name = 'about'

urlpatterns = [
    path(
        'author/',
        TemplateView.as_view(template_name='about/author.html'),
        name='author',
    ),
    path(
        'tech/',
        TemplateView.as_view(template_name='about/tech.html'),
        name='tech'
    ),
]

from django.conf import settings
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import SingleObjectMixin


def page_not_found(request, exception):
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'core/500.html', status=500)


def permission_denied(request, exception):
    return render(request, 'core/403.html', status=403)


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')


class DetailListView(SingleObjectMixin, ListView):
    paginate_by = settings.POSTS_PER_PAGE
    general_object_model = None
    general_object_context_name = None
    relate_objects_name = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(self.general_object_model.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.general_object_context_name] = self.object
        return context

    def get_queryset(self):
        return getattr(self.object, self.relate_objects_name).all()

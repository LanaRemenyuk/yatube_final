from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, 'posts/core/404.html', {'path': request.path}, status=404)


def csrf_failure(request, reason=''):
    return render(request, 'posts/core/403csrf.html')

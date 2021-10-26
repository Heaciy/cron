from django.conf import settings
from django.urls import reverse, resolve
from django.http import HttpResponseRedirect


class LoginRequireMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        print(resolve(request.path).url_name)
        if not (resolve(request.path).url_name in settings.ANONYMOUS_VIEWS or request.user.is_authenticated):
            return HttpResponseRedirect(reverse('login'))
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

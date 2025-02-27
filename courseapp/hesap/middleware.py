# hesap/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            exempt_urls = [
                reverse('hesap:giris'),
                reverse('hesap:kayit'),
            ]
            if request.path not in exempt_urls:
                return redirect('hesap:giris')
        return None
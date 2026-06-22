from urllib.parse import quote

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code != 404 or self._is_exempt(request.path):
            return response

        from website.views import page_not_found

        return page_not_found(request)

    def _is_exempt(self, path):
        prefixes = (
            "/admin/",
            settings.STATIC_URL if settings.STATIC_URL.startswith("/") else f"/{settings.STATIC_URL}",
            "/media/",
        )
        return any(path.startswith(prefix) for prefix in prefixes)


class SiteAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.SITE_ACCESS_ENABLED:
            return self.get_response(request)

        if self._is_exempt(request):
            return self.get_response(request)

        if request.session.get("site_access_granted"):
            return self.get_response(request)

        unlock_url = reverse("site_unlock")
        if request.path == unlock_url:
            return self.get_response(request)

        next_url = quote(request.get_full_path(), safe="/:?=&")
        return redirect(f"{unlock_url}?next={next_url}")

    def _is_exempt(self, request):
        path = request.path
        prefixes = (
            settings.STATIC_URL,
            "/admin/",
            "/ifil-log/",
            "/media/",
        )
        return any(path.startswith(prefix) for prefix in prefixes)

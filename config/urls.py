from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("website.urls")),
    path("", include("cms.urls")),
]

if settings.SERVE_MEDIA:
    from django.views.static import serve
    from django.urls import re_path

    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]

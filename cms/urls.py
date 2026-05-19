from django.contrib.auth import views as auth_views
from django.urls import path

urlpatterns = [
    path(
        "ifil-log/",
        auth_views.LoginView.as_view(template_name="cms/login.html"),
        name="login",
    ),
    path(
        "ifil-log/wyloguj/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
]

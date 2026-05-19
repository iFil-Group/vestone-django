from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path("dostep/", views.site_unlock, name="site_unlock"),
    path("", views.home, name="home"),
    path("produkty/", views.products_list, name="products_list"),
    path(
        "produkty/<slug:slug>/",
        views.product_detail,
        name="product_detail",
    ),
    path("barwy-i-powierzchnie/", views.surfaces, name="surfaces"),
    path("gdzie-kupic/", views.where_to_buy, name="where_to_buy"),
    path("porady/", views.tips, name="tips"),
    path("do-pobrania/", views.downloads, name="downloads"),
    path(
        "o-nas/",
        RedirectView.as_view(url="/o-nas/o-firmie/", permanent=False),
        name="about",
    ),
    path("o-nas/o-firmie/", views.about_company, name="about_company"),
    path("o-nas/aktualnosci/", views.news, name="news"),
    path("o-nas/praca-i-kariera/", views.careers, name="careers"),
    path("o-nas/warunki-gwarancji/", views.warranty, name="warranty"),
    path("o-nas/dla-mediow/", views.media, name="media"),
    path(
        "dokumenty/<slug:slug>/",
        views.document,
        name="document",
    ),
]

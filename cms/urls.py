from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path(
        "ifil-log/",
        views.CMSLoginView.as_view(),
        name="login",
    ),
    path(
        "ifil-log/wyloguj/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path("ifil-log/panel/", views.dashboard, name="cms_dashboard"),
    path("ifil-log/panel/produkty/", views.product_list, name="cms_products"),
    path("ifil-log/panel/produkty/grupa/dodaj/", views.product_group_edit, name="cms_product_group_add"),
    path("ifil-log/panel/produkty/grupa/<int:pk>/", views.product_group_edit, name="cms_product_group_edit"),
    path("ifil-log/panel/produkty/dodaj/", views.product_edit, name="cms_product_add"),
    path("ifil-log/panel/produkty/<int:pk>/", views.product_edit, name="cms_product_edit"),
    path("ifil-log/panel/barwy/", views.surface_list, name="cms_surfaces"),
    path("ifil-log/panel/barwy/dodaj/", views.surface_edit, name="cms_surface_add"),
    path("ifil-log/panel/barwy/<int:pk>/", views.surface_edit, name="cms_surface_edit"),
    path("ifil-log/panel/porady/", views.tip_list, name="cms_tips"),
    path("ifil-log/panel/porady/dodaj/", views.tip_edit, name="cms_tip_add"),
    path("ifil-log/panel/porady/<int:pk>/", views.tip_edit, name="cms_tip_edit"),
    path("ifil-log/panel/aktualnosci/", views.news_list, name="cms_news"),
    path("ifil-log/panel/aktualnosci/dodaj/", views.news_edit, name="cms_news_add"),
    path("ifil-log/panel/aktualnosci/<int:pk>/", views.news_edit, name="cms_news_edit"),
    path("ifil-log/panel/pliki/", views.download_list, name="cms_downloads"),
    path("ifil-log/panel/pliki/kategoria/dodaj/", views.download_category_edit, name="cms_download_category_add"),
    path("ifil-log/panel/pliki/kategoria/<int:pk>/", views.download_category_edit, name="cms_download_category_edit"),
    path("ifil-log/panel/pliki/dodaj/", views.download_item_edit, name="cms_download_add"),
    path("ifil-log/panel/pliki/<int:pk>/", views.download_item_edit, name="cms_download_edit"),
    path("ifil-log/panel/strona/", views.page_index, name="cms_pages"),
    path("ifil-log/panel/strona/blok/dodaj/", views.content_block_edit, name="cms_page_block_add"),
    path("ifil-log/panel/strona/blok/<int:pk>/", views.content_block_edit, name="cms_page_block_edit"),
    path("ifil-log/panel/strona/slajd/dodaj/", views.hero_slide_edit, name="cms_hero_add"),
    path("ifil-log/panel/strona/slajd/<int:pk>/", views.hero_slide_edit, name="cms_hero_edit"),
    path("ifil-log/panel/strona/opinia/dodaj/", views.review_edit, name="cms_review_add"),
    path("ifil-log/panel/strona/opinia/<int:pk>/", views.review_edit, name="cms_review_edit"),
    path("ifil-log/panel/strona/kariera/", views.job_list, name="cms_jobs"),
    path("ifil-log/panel/strona/kariera/dodaj/", views.job_edit, name="cms_job_add"),
    path("ifil-log/panel/strona/kariera/<int:pk>/", views.job_edit, name="cms_job_edit"),
]

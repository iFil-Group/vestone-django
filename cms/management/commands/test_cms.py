import re
from dataclasses import dataclass, field

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse

from cms.models import (
    ContentBlock,
    DownloadCategory,
    DownloadItem,
    HeroSlide,
    JobOpening,
    NewsPost,
    Product,
    ProductGroup,
    Review,
    SiteSettings,
    Tip,
)


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class TestReport:
    results: list[CheckResult] = field(default_factory=list)

    def add(self, name, ok, detail=""):
        self.results.append(CheckResult(name, ok, detail))

    @property
    def passed(self):
        return sum(1 for r in self.results if r.ok)

    @property
    def failed(self):
        return sum(1 for r in self.results if not r.ok)


class Command(BaseCommand):
    help = "Testuje CMS na bieżącej bazie z .env (bez tworzenia testowej bazy)."

    def handle(self, *args, **options):
        report = TestReport()
        client = Client(HTTP_HOST="localhost")
        user = get_user_model().objects.filter(is_active=True).first()

        if user is None:
            self.stderr.write(self.style.ERROR("Brak aktywnego użytkownika w bazie."))
            return

        self._test_auth(client, user, report)
        self._test_get_endpoints(client, user, report)
        self._test_edit_pages(client, user, report)
        self._test_form_posts(client, user, report)
        self._test_ui_markers(client, user, report)

        self.stdout.write("")
        self.stdout.write(self.style.HTTP_INFO("=== Raport testów CMS ==="))
        for result in report.results:
            line = f"[{'OK' if result.ok else 'FAIL'}] {result.name}"
            if result.detail:
                line += f" — {result.detail}"
            if result.ok:
                self.stdout.write(self.style.SUCCESS(line))
            else:
                self.stdout.write(self.style.ERROR(line))

        self.stdout.write("")
        summary = f"Wynik: {report.passed} OK / {report.failed} FAIL / {len(report.results)} razem"
        if report.failed:
            self.stdout.write(self.style.ERROR(summary))
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS(summary))

    def _test_auth(self, client, user, report):
        response = client.get(reverse("login"))
        report.add(
            "GET /ifil-log/",
            response.status_code == 200 and "E-mail" in response.content.decode(),
            f"status={response.status_code}",
        )

        response = client.get(reverse("cms_dashboard"))
        report.add(
            "Panel wymaga logowania",
            response.status_code == 302 and "/ifil-log/" in response.url,
            f"status={response.status_code}, url={response.url}",
        )

        response = client.post(
            reverse("login"),
            {"username": user.email, "password": "wrong-password-123"},
            follow=False,
        )
        report.add(
            "Błędne hasło nie loguje",
            response.status_code == 200 and "Nieprawidłowy e-mail" in response.content.decode(),
            f"status={response.status_code}",
        )

        response = client.post(
            reverse("login") + "?next=/admin/",
            {"username": user.email, "password": "wrong-password-123"},
            follow=False,
        )
        report.add(
            "Logowanie ignoruje next=/admin/",
            response.status_code == 200,
            "brak przekierowania przy złym haśle",
        )

        client.force_login(user)
        response = client.get(reverse("login"), follow=False)
        report.add(
            "Zalogowany użytkownik na /ifil-log/ -> panel",
            response.status_code == 302 and response.url.endswith("/ifil-log/panel/"),
            f"url={response.url}",
        )

        response = client.get(reverse("login") + "?next=/admin/", follow=False)
        report.add(
            "Zalogowany + next=/admin/ -> panel CMS",
            response.status_code == 302 and "/ifil-log/panel/" in response.url,
            f"url={response.url}",
        )

    def _test_get_endpoints(self, client, user, report):
        client.force_login(user)
        endpoints = [
            ("Pulpit", reverse("cms_dashboard")),
            ("Lista produktów", reverse("cms_products")),
            ("Dodaj produkt", reverse("cms_product_add")),
            ("Dodaj grupę produktów", reverse("cms_product_group_add")),
            ("Barwy i powierzchnie", reverse("cms_surfaces")),
            ("Dodaj barwę", reverse("cms_surface_add")),
            ("Porady", reverse("cms_tips")),
            ("Dodaj poradę", reverse("cms_tip_add")),
            ("Aktualności", reverse("cms_news")),
            ("Dodaj aktualność", reverse("cms_news_add")),
            ("Pliki", reverse("cms_downloads")),
            ("Dodaj kategorię plików", reverse("cms_download_category_add")),
            ("Dodaj plik", reverse("cms_download_add")),
            ("Strona", reverse("cms_pages")),
            ("Dodaj blok", reverse("cms_page_block_add")),
            ("Dodaj slajd hero", reverse("cms_hero_add")),
            ("Dodaj opinię", reverse("cms_review_add")),
            ("Kariera", reverse("cms_jobs")),
            ("Dodaj ofertę pracy", reverse("cms_job_add")),
        ]

        for name, url in endpoints:
            response = client.get(url)
            report.add(
                f"GET {name}",
                response.status_code == 200,
                f"status={response.status_code}",
            )

    def _test_edit_pages(self, client, user, report):
        client.force_login(user)
        edit_urls = []

        product = Product.objects.first()
        if product:
            edit_urls.append(("Edycja produktu", reverse("cms_product_edit", args=[product.pk])))

        group = ProductGroup.objects.first()
        if group:
            edit_urls.append(("Edycja grupy", reverse("cms_product_group_edit", args=[group.pk])))

        tip = Tip.objects.first()
        if tip:
            edit_urls.append(("Edycja porady", reverse("cms_tip_edit", args=[tip.pk])))

        news = NewsPost.objects.first()
        if news:
            edit_urls.append(("Edycja aktualności", reverse("cms_news_edit", args=[news.pk])))

        block = ContentBlock.objects.first()
        if block:
            edit_urls.append(("Edycja bloku", reverse("cms_page_block_edit", args=[block.pk])))

        slide = HeroSlide.objects.first()
        if slide:
            edit_urls.append(("Edycja slajdu", reverse("cms_hero_edit", args=[slide.pk])))

        review = Review.objects.first()
        if review:
            edit_urls.append(("Edycja opinii", reverse("cms_review_edit", args=[review.pk])))

        job = JobOpening.objects.first()
        if job:
            edit_urls.append(("Edycja oferty pracy", reverse("cms_job_edit", args=[job.pk])))

        category = DownloadCategory.objects.first()
        if category:
            edit_urls.append(
                ("Edycja kategorii plików", reverse("cms_download_category_edit", args=[category.pk]))
            )

        item = DownloadItem.objects.first()
        if item:
            edit_urls.append(("Edycja pliku", reverse("cms_download_edit", args=[item.pk])))

        for name, url in edit_urls:
            response = client.get(url)
            html = response.content.decode()
            ok = response.status_code == 200 and "cms-form" in html
            report.add(f"GET {name}", ok, f"status={response.status_code}")

        if product:
            response = client.get(reverse("cms_product_edit", args=[product.pk]))
            html = response.content.decode()
            report.add(
                "Formularz produktu ma edytor pinów",
                "data-pin-editor" in html and "cms-file" in html,
            )
            report.add(
                "Formularz produktu ma formset parametrów",
                'name="specs-TOTAL_FORMS"' in html,
            )

    def _test_form_posts(self, client, user, report):
        client.force_login(user)

        settings = SiteSettings.load()
        response = client.post(
            reverse("cms_pages"),
            {
                "phone": settings.phone,
                "email": settings.email,
                "infoline": settings.infoline,
                "address": settings.address,
                "footer_tagline": settings.footer_tagline,
            },
            follow=False,
        )
        report.add(
            "POST ustawienia strony",
            response.status_code == 302 and response.url.endswith("/ifil-log/panel/strona/"),
            f"status={response.status_code}",
        )

        review = Review.objects.first()
        if review:
            response = client.post(
                reverse("cms_review_edit", args=[review.pk]),
                {
                    "quote": review.quote,
                    "author": review.author,
                    "sort_order": review.sort_order,
                    "is_active": "on" if review.is_active else "",
                },
                follow=False,
            )
            report.add(
                "POST edycja opinii",
                response.status_code == 302,
                f"status={response.status_code}",
            )

        job = JobOpening.objects.first()
        if job:
            response = client.post(
                reverse("cms_job_edit", args=[job.pk]),
                {
                    "title": job.title,
                    "slug": job.slug,
                    "location": job.location,
                    "employment_type": job.employment_type,
                    "excerpt": job.excerpt,
                    "body": job.body,
                    "is_active": "on" if job.is_active else "",
                },
                follow=False,
            )
            report.add(
                "POST edycja oferty pracy",
                response.status_code == 302,
                f"status={response.status_code}",
            )

        category = DownloadCategory.objects.first()
        if category:
            response = client.post(
                reverse("cms_download_category_edit", args=[category.pk]),
                {
                    "label": category.label,
                    "slug": category.slug,
                    "sort_order": category.sort_order,
                },
                follow=False,
            )
            report.add(
                "POST edycja kategorii plików",
                response.status_code == 302,
                f"status={response.status_code}",
            )

        tip = Tip.objects.first()
        if tip:
            response = client.post(
                reverse("cms_tip_edit", args=[tip.pk]),
                {
                    "title": tip.title,
                    "slug": tip.slug,
                    "excerpt": tip.excerpt,
                    "body": tip.body,
                    "published_at": tip.published_at.isoformat(),
                    "is_published": "on" if tip.is_published else "",
                },
                follow=False,
            )
            report.add(
                "POST edycja porady",
                response.status_code == 302,
                f"status={response.status_code}",
            )

        news = NewsPost.objects.first()
        if news:
            response = client.post(
                reverse("cms_news_edit", args=[news.pk]),
                {
                    "title": news.title,
                    "slug": news.slug,
                    "excerpt": news.excerpt,
                    "body": news.body,
                    "published_at": news.published_at.isoformat(),
                    "is_published": "on" if news.is_published else "",
                },
                follow=False,
            )
            report.add(
                "POST edycja aktualności",
                response.status_code == 302,
                f"status={response.status_code}",
            )

        product = Product.objects.prefetch_related("specs", "pins", "gallery").first()
        if product:
            get_response = client.get(reverse("cms_product_edit", args=[product.pk]))
            html = get_response.content.decode()
            post_data = self._build_product_post_data(product, html)
            response = client.post(
                reverse("cms_product_edit", args=[product.pk]),
                post_data,
                follow=False,
            )
            report.add(
                "POST edycja produktu (form + formsety)",
                response.status_code == 302 and "/ifil-log/panel/produkty/" in response.url,
                f"status={response.status_code}, url={getattr(response, 'url', '')}",
            )

        response = client.post(
            reverse("cms_product_add"),
            {
                "group": ProductGroup.objects.first().pk,
                "title": "",
                "slug": "",
            },
            follow=True,
        )
        report.add(
            "Walidacja pustego produktu",
            response.status_code == 200 and "cms-field--error" in response.content.decode(),
            f"status={response.status_code}",
        )

    def _test_ui_markers(self, client, user, report):
        client.force_login(user)
        response = client.post(
            reverse("cms_pages"),
            {
                "phone": SiteSettings.load().phone,
                "email": SiteSettings.load().email,
                "infoline": SiteSettings.load().infoline,
                "address": SiteSettings.load().address,
                "footer_tagline": SiteSettings.load().footer_tagline,
            },
            follow=True,
        )
        html = response.content.decode()
        report.add(
            "Toast po zapisie (messages)",
            "cms-toast-stack" in html and "data-cms-toast" in html,
        )
        report.add(
            "Panel ma stały sidebar",
            "cms-sidebar" in html and "cms-topbar" in html,
        )
        report.add(
            "Skrypt toastów załadowany",
            "cms-toasts.js" in html,
        )

        response = client.get(reverse("cms_product_add"))
        html = response.content.decode()
        report.add(
            "Formularz ma stylowane pola plików",
            "cms-file__button" in html,
        )
        report.add(
            "Skrypt pól plików załadowany",
            "cms-file-inputs.js" in html,
        )

    def _build_product_post_data(self, product, html):
        data = {
            "group": str(product.group_id),
            "title": product.title,
            "slug": product.slug,
            "subtitle": product.subtitle,
            "description": product.description,
            "description_extra": product.description_extra,
            "sort_order": str(product.sort_order),
        }
        if product.is_active:
            data["is_active"] = "on"

        for prefix in ("specs", "pins", "gallery"):
            total = self._input_value(html, f"{prefix}-TOTAL_FORMS")
            initial = self._input_value(html, f"{prefix}-INITIAL_FORMS")
            min_num = self._input_value(html, f"{prefix}-MIN_NUM_FORMS")
            max_num = self._input_value(html, f"{prefix}-MAX_NUM_FORMS")
            if total is not None:
                data[f"{prefix}-TOTAL_FORMS"] = total
            if initial is not None:
                data[f"{prefix}-INITIAL_FORMS"] = initial
            if min_num is not None:
                data[f"{prefix}-MIN_NUM_FORMS"] = min_num
            if max_num is not None:
                data[f"{prefix}-MAX_NUM_FORMS"] = max_num

        for index, spec in enumerate(product.specs.order_by("sort_order", "id")):
            data[f"specs-{index}-id"] = str(spec.pk)
            data[f"specs-{index}-label"] = spec.label
            data[f"specs-{index}-value"] = spec.value
            data[f"specs-{index}-sort_order"] = str(spec.sort_order)

        spec_total = int(data.get("specs-TOTAL_FORMS", product.specs.count()))
        for index in range(product.specs.count(), spec_total):
            data[f"specs-{index}-label"] = ""
            data[f"specs-{index}-value"] = ""
            data[f"specs-{index}-sort_order"] = "0"

        for index, pin in enumerate(product.pins.order_by("sort_order", "id")):
            data[f"pins-{index}-id"] = str(pin.pk)
            data[f"pins-{index}-x"] = str(pin.x)
            data[f"pins-{index}-y"] = str(pin.y)
            data[f"pins-{index}-text"] = pin.text
            data[f"pins-{index}-sort_order"] = str(pin.sort_order)

        for index, image in enumerate(product.gallery.order_by("sort_order", "id")):
            data[f"gallery-{index}-id"] = str(image.pk)
            data[f"gallery-{index}-alt"] = image.alt
            data[f"gallery-{index}-sort_order"] = str(image.sort_order)

        gallery_total = int(data.get("gallery-TOTAL_FORMS", product.gallery.count()))
        for index in range(product.gallery.count(), gallery_total):
            data[f"gallery-{index}-alt"] = ""
            data[f"gallery-{index}-sort_order"] = "0"

        return data

    def _input_value(self, html, name):
        match = re.search(rf'name="{re.escape(name)}" value="([^"]*)"', html)
        if match:
            return match.group(1)
        match = re.search(rf'name="{re.escape(name)}" value=\'([^\']*)\'', html)
        if match:
            return match.group(1)
        return None

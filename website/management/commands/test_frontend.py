from dataclasses import dataclass, field

from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse

from cms.models import DownloadItem, NewsPost, Product, ProductGroup, Tip
from cms.services import (
    category_products,
    get_download_items,
    get_home_context,
    get_news,
    get_product,
    get_product_groups,
    get_tips,
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
        return sum(1 for result in self.results if result.ok)

    @property
    def failed(self):
        return sum(1 for result in self.results if not result.ok)


class Command(BaseCommand):
    help = "Testuje front publiczny na bieżącej bazie z .env."

    def handle(self, *args, **options):
        report = TestReport()
        client = self._client_with_access()

        self._test_services(report)
        self._test_public_pages(client, report)
        self._test_cms_content_on_pages(client, report)
        self._test_filtering_markup(client, report)
        self._test_not_found(client, report)

        self.stdout.write("")
        self.stdout.write(self.style.HTTP_INFO("=== Raport testów frontu ==="))
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

    def _client_with_access(self):
        client = Client(HTTP_HOST="localhost")
        session = client.session
        session["site_access_granted"] = True
        session.save()
        return client

    def _test_services(self, report):
        groups = get_product_groups()
        report.add("Serwis: grupy produktów", len(groups) >= 1, f"count={len(groups)}")

        group = ProductGroup.objects.filter(is_active=True).first()
        if group:
            products = category_products(group.slug)
            report.add(
                f"Serwis: produkty kategorii {group.slug}",
                len(products) >= 1 and all("search_text" in item for item in products),
                f"count={len(products)}",
            )
            product = Product.objects.filter(group=group, is_active=True).first()
            if product:
                data = get_product(group.slug, product.slug)
                report.add(
                    "Serwis: szczegóły produktu z CMS",
                    data is not None and "specs" in data and "pins" in data,
                    product.slug,
                )

        tips = get_tips()
        report.add("Serwis: porady", len(tips) >= 1, f"count={len(tips)}")

        news = get_news()
        report.add("Serwis: aktualności", len(news) >= 1, f"count={len(news)}")

        downloads = get_download_items()
        report.add("Serwis: pliki do pobrania", len(downloads) >= 1, f"count={len(downloads)}")

        home = get_home_context()
        report.add(
            "Serwis: kontekst strony głównej",
            "hero_slides" in home and "reviews" in home and len(home["product_groups"]) >= 1,
        )

    def _test_public_pages(self, client, report):
        pages = [
            ("Strona główna", reverse("home")),
            ("Produkty", reverse("products_list")),
            ("Barwy i powierzchnie", reverse("surfaces")),
            ("Gdzie kupić", reverse("where_to_buy")),
            ("Porady", reverse("tips")),
            ("Do pobrania", reverse("downloads")),
            ("Aktualności", reverse("news")),
            ("Kariera", reverse("careers")),
            ("Warunki gwarancji", reverse("warranty")),
            ("Dla mediów", reverse("media")),
        ]

        group = ProductGroup.objects.filter(is_active=True).first()
        if group:
            pages.append((f"Kategoria {group.slug}", reverse("product_category", args=[group.slug])))

        product = Product.objects.filter(is_active=True).select_related("group").first()
        if product:
            pages.append(
                (
                    f"Produkt {product.slug}",
                    reverse(
                        "product_detail",
                        args=[product.group.slug, product.slug],
                    ),
                )
            )

        tip = Tip.objects.filter(is_published=True).first()
        if tip:
            pages.append(("Porada", reverse("tip_detail", args=[tip.slug])))

        post = NewsPost.objects.filter(is_published=True).first()
        if post:
            pages.append(("Aktualność", reverse("news_detail", args=[post.slug])))

        for name, url in pages:
            response = client.get(url)
            report.add(f"GET {name}", response.status_code == 200, f"status={response.status_code}")

    def _test_cms_content_on_pages(self, client, report):
        product = Product.objects.filter(is_active=True).select_related("group").first()
        if product:
            response = client.get(
                reverse("product_detail", args=[product.group.slug, product.slug])
            )
            html = response.content.decode()
            report.add(
                "Produkt CMS na stronie szczegółów",
                product.title in html,
                product.title,
            )
            report.add(
                "Piny produktu na stronie szczegółów",
                "product-pin" in html or "data-product-pins" in html,
            )

        tip = Tip.objects.filter(is_published=True).first()
        if tip:
            response = client.get(reverse("tip_detail", args=[tip.slug]))
            report.add("Porada CMS na stronie", tip.title in response.content.decode(), tip.title)

        response = client.get(reverse("downloads"))
        html = response.content.decode()
        item = DownloadItem.objects.filter(is_published=True).first()
        if item:
            report.add(
                "Pliki CMS na stronie pobierania",
                item.title in html and "data-download-item" in html,
                item.title,
            )

        response = client.get(reverse("home"))
        html = response.content.decode()
        report.add("Strona główna ma sekcje CMS", "home-hero" in html or "home-reviews" in html)

    def _test_filtering_markup(self, client, report):
        group = ProductGroup.objects.filter(is_active=True).first()
        if group:
            response = client.get(reverse("product_category", args=[group.slug]))
            html = response.content.decode()
            report.add(
                "Kategoria: filtry w HTML",
                "data-product-filters" in html and "data-product-search" in html,
            )
            report.add(
                "Kategoria: skrypt filtrów",
                "product-filters.js" in html,
            )
            report.add(
                "Kategoria: dane do wyszukiwania",
                "data-search=" in html,
            )
            product = Product.objects.filter(group=group, is_active=True).first()
            if product:
                report.add(
                    "Kategoria: tytuł produktu widoczny",
                    product.title in html,
                    product.title,
                )

        response = client.get(reverse("downloads"))
        html = response.content.decode()
        report.add(
            "Pobrania: wyszukiwanie i filtry kategorii",
            "data-downloads-search" in html and "data-downloads-category" in html,
        )
        report.add(
            "Pobrania: skrypt filtrowania",
            "downloads.js" in html,
        )
        report.add(
            "Pobrania: atrybuty data-search na plikach",
            "data-search=" in html,
        )

        response = client.get(reverse("surfaces"))
        html = response.content.decode()
        report.add(
            "Barwy: skrypt filtrów",
            "product-filters.js" in html,
        )

    def _test_not_found(self, client, report):
        response = client.get("/nie-istniejacy-adres-testowy/")
        html = response.content.decode()
        report.add(
            "404 niestniejącej strony",
            response.status_code == 404 and "Taka strona nie istnieje" in html,
            f"status={response.status_code}",
        )

        response = client.get("/produkty/nie-ma-takiej-kategorii/")
        report.add("404 nieistniejącej kategorii", response.status_code == 404)

        response = client.get("/porady/nie-ma-takiej-porady/")
        report.add("404 nieistniejącej porady", response.status_code == 404)

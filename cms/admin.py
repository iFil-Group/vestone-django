from django.contrib import admin

from .models import (
    ContentBlock,
    DownloadCategory,
    DownloadItem,
    HeroSlide,
    JobOpening,
    NewsPost,
    Product,
    ProductGalleryImage,
    ProductGroup,
    ProductPin,
    ProductSpec,
    Review,
    SiteSettings,
    SurfaceItem,
    Tip,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


admin.site.register(ContentBlock)
admin.site.register(HeroSlide)
admin.site.register(Review)
admin.site.register(ProductGroup)
admin.site.register(Product)
admin.site.register(ProductSpec)
admin.site.register(ProductPin)
admin.site.register(ProductGalleryImage)
admin.site.register(SurfaceItem)
admin.site.register(Tip)
admin.site.register(NewsPost)
admin.site.register(DownloadCategory)
admin.site.register(DownloadItem)
admin.site.register(JobOpening)

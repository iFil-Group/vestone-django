from django.contrib import admin

from .models import (
    ContentBlock,
    DownloadCategory,
    DownloadItem,
    HeroSlide,
    JobOpening,
    JobApplication,
    LegalDocument,
    NewsPost,
    NewsGalleryImage,
    Product,
    ProductGalleryImage,
    ProductPackshotImage,
    ProductGroup,
    ProductPin,
    ProductAttribute,
    ProductAttributeAssignment,
    ProductAttributeOption,
    ProductSpec,
    Review,
    SiteSettings,
    SurfaceItem,
    SurfaceCategory,
    SurfaceType,
    Tip,
    TipGalleryImage,
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
admin.site.register(ProductAttribute)
admin.site.register(ProductAttributeOption)
admin.site.register(ProductAttributeAssignment)
admin.site.register(ProductSpec)
admin.site.register(ProductPin)
admin.site.register(ProductGalleryImage)
admin.site.register(ProductPackshotImage)
admin.site.register(SurfaceItem)
admin.site.register(SurfaceCategory)
admin.site.register(SurfaceType)
admin.site.register(Tip)
admin.site.register(NewsPost)
admin.site.register(DownloadCategory)
admin.site.register(DownloadItem)
admin.site.register(JobOpening)
admin.site.register(JobApplication)
admin.site.register(LegalDocument)
admin.site.register(TipGalleryImage)
admin.site.register(NewsGalleryImage)

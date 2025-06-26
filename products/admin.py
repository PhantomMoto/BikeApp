from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from .models import BikeBrand, BikeModel, Category, Accessory, Blog, YouTubeVideo, Message


class AccessoryAdminForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = '__all__'

class AccessoryAdmin(admin.ModelAdmin):
    form = AccessoryAdminForm
    list_display = ['name', 'price', 'is_universal', 'preview_img']
    filter_horizontal = ['bike_models']
    fields = ['name', 'price', 'is_universal', 'image_url', 'bike_models', 'categories', 'description']  # image_url add kar

    def preview_img(self, obj):
        if obj.image_url:
            return mark_safe(f'<img src="{obj.image_url}" width="80" />')
        return "-"
    preview_img.short_description = "Image Preview"
    class Media:
        js = ('js/accessory_admin.js',)  # agar bike_models ko disable karna hai jab is_universal tick ho


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'preview_img']

    def preview_img(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="80" />')
        return "-"
    preview_img.short_description = "Image"

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "published_at", "preview_img")
    search_fields = ("title", "content")
    date_hierarchy = "published_at"

    def preview_img(self, obj):
        if obj.thumbnail:
            return mark_safe(f'<img src="{obj.thumbnail.url}" width="80" />')
        return "-"
    preview_img.short_description = "Thumbnail"


@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(admin.ModelAdmin):
    list_display = ("title", "video_url", "preview_img")
    search_fields = ("title",)

    def preview_img(self, obj):
        if obj.thumbnail:
            return mark_safe(f'<img src="{obj.thumbnail.url}" width="80" />')
        return "-"
    preview_img.short_description = "Thumbnail"


admin.site.register(BikeBrand)
admin.site.register(BikeModel)
admin.site.register(Accessory, AccessoryAdmin)
admin.site.register(Message)

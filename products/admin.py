from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Accessory, Blog, Category, YouTubeVideo, BikeBrand, BikeModel

### Accessory Admin ###
@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_universal', 'preview_img']
    search_fields = ['name']
    list_filter = ['is_universal', 'bike_models', 'categories']

    def preview_img(self, obj):
        if obj.image_url:
            return mark_safe(f'<img src="{obj.image_url}" width="80" />')
        return "No Image"
    preview_img.short_description = "Image Preview"

### Blog Admin ###
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title','preview_img']
    search_fields = ['title', 'content']

    def preview_img(self, obj):
        if obj.thumbnail_url:
            return mark_safe(f'<img src="{obj.thumbnail_url}" width="80" />')
        return "No Image"
    preview_img.short_description = "Image Preview"

### Category Admin ###
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'preview_img']
    search_fields = ['name']

    def preview_img(self, obj):
        if obj.image_url:
            return mark_safe(f'<img src="{obj.image_url}" width="80" />')
        return "No Image"
    preview_img.short_description = "Image Preview"

### YouTube Video Admin ###
@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'video_url', 'preview_img']
    search_fields = ['title', 'video_url']

    def preview_img(self, obj):
        if obj.thumbnail_url:
            return mark_safe(f'<img src="{obj.thumbnail_url}" width="80" />')
        return "No Thumbnail"
    preview_img.short_description = "Thumbnail Preview"

### Bike Brand Admin ###
@admin.register(BikeBrand)
class BikeBrandAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

### Bike Model Admin ###
@admin.register(BikeModel)
class BikeModelAdmin(admin.ModelAdmin):
    list_display = ['brand', 'name']
    search_fields = ['name']
    list_filter = ['brand']

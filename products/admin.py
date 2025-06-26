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
    list_display = ['name', 'price', 'is_universal']
    filter_horizontal = ['bike_models']
    fields = ['name', 'price', 'is_universal', 'image', 'bike_models', 'categories', 'description']  # image_url add kar

   
    class Media:
        js = ('js/accessory_admin.js',)  # agar bike_models ko disable karna hai jab is_universal tick ho


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name',]

   

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "published_at")
    search_fields = ("title", "content")
    date_hierarchy = "published_at"

   


@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(admin.ModelAdmin):
    list_display = ("title", "video_url")
    search_fields = ("title",)

    

admin.site.register(BikeBrand)
admin.site.register(BikeModel)
admin.site.register(Accessory, AccessoryAdmin)
admin.site.register(Message)

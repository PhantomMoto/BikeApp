from django.contrib import admin
from django import forms
from .models import BikeBrand, BikeModel, Category, Accessory, Blog, YouTubeVideo


from django.contrib import admin
from django import forms
from .models import Accessory

class AccessoryAdminForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit)
        print("Uploaded Image URL:", instance.image.url)
        return instance

class AccessoryAdmin(admin.ModelAdmin):
    form = AccessoryAdminForm

admin.site.register(Accessory, AccessoryAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'image']

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
admin.site.register(Accessory, AccessoryAdmin)  # ✅ FIXED


from django.contrib import admin
from .models import Message

admin.site.register(Message)

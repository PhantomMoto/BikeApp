from django.contrib import admin
from django import forms
from .models import BikeBrand, BikeModel, Category, Accessory, Blog, YouTubeVideo, Message
from django.core.files.storage import default_storage

# ---
# NOTE: On Render, uploaded images are saved to /persistent_media/ (MEDIA_ROOT)
# This admin form ensures images are saved to the correct location and old images are deleted on update.
# After redeploy, files in /persistent_media/ will persist ONLY if Render persistent disk is correctly mounted.
# ---

class AccessoryAdminForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = '__all__'
    def save(self, commit=True):
        instance = super().save(commit)
        # Ensure the image is saved to persistent storage
        if instance.image and not default_storage.exists(instance.image.name):
            instance.image.save(instance.image.name, instance.image.file, save=False)
        return instance

class AccessoryAdmin(admin.ModelAdmin):
    form = AccessoryAdminForm
    list_display = ['name', 'price', 'is_universal']
    filter_horizontal = ['bike_models']

    def save_model(self, request, obj, form, change):
        # Delete old image file if a new one is uploaded
        if change and 'image' in form.changed_data:
            try:
                old_obj = Accessory.objects.get(pk=obj.pk)
                if old_obj.image and old_obj.image.name != obj.image.name:
                    old_obj.image.delete(save=False)
            except Accessory.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)

    class Media:
        js = ('js/accessory_admin.js',)

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
admin.site.register(Accessory, AccessoryAdmin)
admin.site.register(Message)

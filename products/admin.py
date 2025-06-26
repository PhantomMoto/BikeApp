from django.contrib import admin
from django import forms
from .models import BikeBrand, BikeModel, Category, Accessory, Blog, YouTubeVideo, Message
from django.core.files.storage import default_storage


class AccessoryAdminForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = '__all__'
    def save(self, commit=True):
        instance = super().save(commit)
        print("Uploaded Image URL:", instance.image.url)
        if instance.image and not default_storage.exists(instance.image.name):
            instance.image.save(instance.image.name, instance.image.file, save=False)
        return instance
    def save_model(self, request, obj, form, change):
        if change and 'image' in form.changed_data:
            try:
                old_obj = Accessory.objects.get(pk=obj.pk)
                if old_obj.image and old_obj.image.url != obj.image.url:
                    old_obj.image.delete(save=False)
            except Accessory.DoesNotExist:
                pass
        obj.save()
        # return instance


class AccessoryAdmin(admin.ModelAdmin):
    form = AccessoryAdminForm
    list_display = ['name', 'price', 'is_universal']
    filter_horizontal = ['bike_models']

    class Media:
        js = ('js/accessory_admin.js',)  # agar koi custom JS laga rahe ho


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


# Directly register these without custom admin
admin.site.register(BikeBrand)
admin.site.register(BikeModel)
admin.site.register(Accessory, AccessoryAdmin)
admin.site.register(Message)

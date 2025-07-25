from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Accessory, Blog, Category, YouTubeVideo, BikeBrand, BikeModel, FeaturedProduct, Color

### Accessory Admin ###
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Accessory

from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Accessory, Blog, Category, YouTubeVideo, BikeBrand, BikeModel, FeaturedProduct, Color,SlideshowImage

# products/admin.py

from django.contrib import admin
from .models import Message

@admin.register(SlideshowImage)
class SlideshowImageAdmin(admin.ModelAdmin):
    list_display = ('order', 'caption')
    ordering = ('order',)
@admin.register(Message)
class SlideshowImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'message')

from django.contrib import admin
from .models import CustomerFeedback

@admin.register(CustomerFeedback)
class CustomerFeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'uploaded_at']


class AccessoryAdminForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        # Ab koi validation nahi — sab optional bhai, jo bhi daalna chahe daale.
        return cleaned_data
@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    form = AccessoryAdminForm
    list_display = ['name', 'mrp', 'offer_price', 'discount_percent', 'stock', 'is_universal', 'preview_img', 'is_COD']
    search_fields = ['name', "is_COD"]
    list_filter = ['is_universal', 'bike_models', 'categories', "is_COD"]
    filter_horizontal = ['categories', 'bike_models', 'colors']
    fieldsets = (
        (None, {
            'fields': (
                'image', 'name', 'colors',
                'subimage1', 'subimage2', 'subimage3', 'subimage4', 'subimage5',  # ← add ye line
                'shipment_width', 'shipment_height', 'shipment_weight', 'shipment_length',
                'mrp', 'offer_price', 'discount_percent',
                'stock', 'categories',
                'bike_models', 'is_universal',
                'description', 'large_description', 'slug', 'is_COD'
            ),
        }),
    )
    prepopulated_fields = {"slug": ("name",)}

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Categories ko default add karne ka code hata do bhi, warna confuse hoga
        # Kyunki validation nahi hai ab, ye bhi hata dete hain
        # pass karte hain yahan

    def preview_img(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="width:80px; height:auto; border-radius:4px;" />')
        return "No Image"
    preview_img.short_description = "Image Preview"

    


### Featured Product Admin ###
@admin.register(FeaturedProduct)
class FeaturedProductAdmin(admin.ModelAdmin):
    filter_horizontal = ['accessories']
    list_display = ['featured_at', 'get_accessories']
    search_fields = ['accessories__name']
    list_filter = ['featured_at']
    def get_accessories(self, obj):
        return ", ".join([a.name for a in obj.accessories.all()])
    get_accessories.short_description = "Accessories"

### Blog Admin ###
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title','preview_img']
    search_fields = ['title', 'content']

    def preview_img(self, obj):
        if obj.thumbnail:
            return mark_safe(f'<img src="{obj.thumbnail.url}" width="80" />')
        return "No Image"
    preview_img.short_description = "Image Preview"

### Category Admin ###
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'preview_img']
    search_fields = ['name']
    def preview_img(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="80" />')
        return "No Image"
    preview_img.short_description = "Image Preview"

### YouTube Video Admin ###
@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'video_url', 'preview_img']
    search_fields = ['title', 'video_url']

    def preview_img(self, obj):
        if obj.thumbnail:
            return mark_safe(f'<img src="{obj.thumbnail.url}" width="80" />')
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

### Color Admin ###
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'hex_code', 'color_preview']
    search_fields = ['name', 'hex_code']
    def color_preview(self, obj):
        return mark_safe(f'<span style="display:inline-block;width:24px;height:24px;background:{obj.hex_code};border-radius:50%;border:1px solid #ccc;"></span>')
    color_preview.short_description = "Preview"
from django.contrib import admin
from .models import Order


## Order Admin
# Register the Order model with the admin site
from django.contrib import admin
from .models import Order


from django import forms
from .models import Accessory



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'amount', 'status', 'created_at', 'waybill')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'user__username', 'waybill', 'products_desc')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Order Details', {
            'fields': ('order_id', 'waybill', 'amount', 'products_desc', 'status')
        }),
        ('Customer Info', {
            'fields': ('user', 'address')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

    def has_add_permission(self, request):
        # Prevent adding orders manually from admin
        return False

    def has_delete_permission(self, request, obj=None):
        # Optional: Disable delete if you want full record keeping
        return True

from django.db import models
from django.utils.text import slugify

class BikeBrand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class BikeModel(models.Model):
    brand = models.ForeignKey(BikeBrand, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('brand', 'name')

    def __str__(self):
        return f"{self.brand.name} {self.name}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    hex_code = models.CharField(max_length=7, help_text="Hex code, e.g. #ff0000")

    def __str__(self):
        return self.name


class Accessory(models.Model):
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to='accessory_images/', blank=True, null=True)
    colors = models.ManyToManyField(Color, related_name='accessories', blank=True)
    shipment_width = models.FloatField(default=0.0)    # cm ya inch, jo bhi unit
    shipment_height = models.FloatField(default=0.0)    
    shipment_weight = models.FloatField(default=0.0)  # kg ya grams, jo bhi unit
    shipment_length = models.FloatField(default=0.0)  # kg ya grams, jo bhi unit
    mrp = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='MRP')
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Offer Price')
    discount_percent = models.PositiveIntegerField(blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='accessories',blank=True)
    bike_models = models.ManyToManyField(BikeModel, related_name='accessories',blank=True)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    large_description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    is_universal = models.BooleanField(default=False)
    is_COD = models.BooleanField(default=True, verbose_name='Cash on Delivery Available')

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            n = 1
            while Accessory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        name = self.name
        return f"{name} ({self.offer_price})" if self.offer_price else name
       


class Blog(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    thumbnail = models.ImageField(upload_to='blog_thumbnails/', blank=True, null=True)
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class YouTubeVideo(models.Model):
    title = models.CharField(max_length=200)
    video_url = models.URLField()
    thumbnail = models.ImageField(upload_to='youtube_thumbnails/', blank=True, null=True)

    def __str__(self):
        return self.title


class Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
from django.contrib.auth.models import User

class FeaturedProduct(models.Model):
    accessories = models.ManyToManyField(Accessory, related_name='featured_in')
    featured_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Featured: {', '.join([a.name for a in self.accessories.all()])}"
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_id = models.CharField(max_length=50)
    waybill = models.CharField(max_length=50)
    amount = models.FloatField()
    products_desc = models.TextField()
    address = models.TextField()
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_id} - {self.user.username}"
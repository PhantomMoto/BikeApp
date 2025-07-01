from django.db import models
# from imagekit.models import ProcessedImageField
# from imagekit.processors import ResizeToFill

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
    size = models.CharField(max_length=50, blank=True, null=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='MRP')
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Offer Price')
    discount_percent = models.PositiveIntegerField(blank=True, null=True)
    shipping_category = models.CharField(max_length=20, choices=[('1kg','1kg'),('2kg','2kg'),('3kg','3kg'),('4kg','4kg'),('5kg','5kg')], blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='accessories')
    bike_models = models.ManyToManyField(BikeModel, related_name='accessories')
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_universal = models.BooleanField(default=False)
    size = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        name = self.name
        color_names = ', '.join([c.name for c in self.colors.all()])
        if color_names:
            name += f" ({color_names})"
        if self.size:
            name += f" {self.size}"
        return name


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


class FeaturedProduct(models.Model):
    accessories = models.ManyToManyField(Accessory, related_name='featured_in')
    featured_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Featured: {', '.join([a.name for a in self.accessories.all()])}"

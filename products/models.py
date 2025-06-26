from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

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
    # ImageKit ProcessedImageField - uploads image, processes (resize etc.) automatically
    image = ProcessedImageField(
        upload_to='category_images/',
        processors=[ResizeToFill(300, 300)],  # Resize to 300x300 px square
        format='JPEG',
        options={'quality': 80},
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


class Accessory(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    categories = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    bike_models = models.ManyToManyField(BikeModel, related_name='accessories')
    created_at = models.DateTimeField(auto_now_add=True)
    image = ProcessedImageField(
        upload_to='accessories/',
        processors=[ResizeToFill(600, 400)],
        format='JPEG',
        options={'quality': 85},
        null=True,
        blank=True
    )
    is_universal = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Blog(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    thumbnail = ProcessedImageField(
        upload_to='blog_thumbnails/',
        processors=[ResizeToFill(800, 450)],
        format='JPEG',
        options={'quality': 85},
        null=True,
        blank=True
    )
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class YouTubeVideo(models.Model):
    title = models.CharField(max_length=200)
    video_url = models.URLField()
    thumbnail = ProcessedImageField(
        upload_to='video_thumbnails/',
        processors=[ResizeToFill(800, 450)],
        format='JPEG',
        options={'quality': 85},
        null=True,
        blank=True
    )

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

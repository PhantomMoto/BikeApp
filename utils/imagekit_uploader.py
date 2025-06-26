# utils/imagekit_uploader.py

from imagekitio import ImageKit
from django.conf import settings

imagekit = ImageKit(
    private_key=settings.IMAGEKIT_PRIVATE_KEY,
    public_key=settings.IMAGEKIT_PUBLIC_KEY,
    url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
)

def upload_image(file, file_name=None):
    upload = imagekit.upload(
        file=file,
        file_name=file_name or file.name,
    )
    return upload['response']['url']

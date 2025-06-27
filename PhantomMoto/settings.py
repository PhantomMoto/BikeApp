from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-*p3gkb&fy!1k(51q+hvnl%t#o=5pvf2z9keqnjg(x4jh0qcg3y'
DEBUG = os.environ.get('DEBUG')

ALLOWED_HOSTS = ['phantommoto.in', 'www.phantommoto.in', '127.0.0.1', 'localhost','https://bikeapp-440n.onrender.com/']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'products',
    'django.contrib.sitemaps',
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static file optimization
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'PhantomMoto.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'PhantomMoto.wsgi.application'

import os
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}


# delivery settings
# Make sure to set these environment variables in your production environment
# or replace with your actual values
DELHIVERY_API_TOKEN = '77e3075e4a4235202652825b86a907b174a823be'
DELHIVERY_CLIENT = 'PHANTOM_MOTO NA'



AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# STATIC FILES
STATIC_URL = '/static/'
STATICFILES_DIRS = [ BASE_DIR / 'static' ]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
import os
BASE_DIR = Path(__file__).resolve().parent.parent


import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_URL = '/media/'
MEDIA_ROOT = '/persistent_media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 🔐 SECURITY HEADERS (for production)
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ✅ LOGIN CONFIG
LOGIN_REDIRECT_URL = 'products:product_list'
LOGOUT_REDIRECT_URL = 'products:login'
rzpkid = os.environ.get('RAZORPAY_KEY_ID')
rzpkst = os.environ.get('RAZORPAY_KEY_SECRET')
# 🪙 RAZORPAY KEYS
RAZORPAY_KEY_ID = 'rzp_test_cq7lxIhKWEMmCZ'
RAZORPAY_KEY_SECRET = 'JlTRultMrU8OS7izPky8fgqV'

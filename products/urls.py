"""
URL configuration for PhantomMoto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

app_name = 'products'

urlpatterns = [
    path('', views.home),
    path('products/', views.product_list),
    path('ajax/get-models/', views.get_models_by_brand, name='get_models_by_brand'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    # path('login/', auth_views.LoginView.as_view(template_name='products/login.html'), name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='products:login'), name='logout'),
    path('register/', views.register, name='register'),
    path('account/', views.account_view, name='account'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:accessory_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:accessory_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:accessory_id>/', views.cart_update, name='cart_update'),
    path('ajax/cart/add/<int:accessory_id>/', views.ajax_cart_add, name='ajax_cart_add'),
    path('ajax/cart/count/', views.ajax_cart_count, name='ajax_cart_count'),
    path('ajax/cart/items/', views.ajax_cart_items, name='ajax_cart_items'),
    path('ajax/cart/update/<int:accessory_id>/', views.ajax_cart_update, name='ajax_cart_update'),
    path('razorpay/create-order/', views.create_razorpay_order, name='razorpay_create_order'),
    path('razorpay/verify/', views.verify_razorpay_payment, name='razorpay_verify'),
    path('contact/', views.contact_view, name='contact'),
    path('blog/', views.blog_list_view, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail_view, name='blog_detail'),
    path('contact/', views.contact_view, name='contact'),
     path('post-payment/', views.submit_to_delhivery, name='post_payment'),
    path('submit-to-delhivery/', views.submit_to_delhivery, name='submit_to_delhivery'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category-pdf/', views.category_pdf, name='category_pdf'),
    path('shipping_form/', views.shipping_form, name='shipping_form'),
    path('order_summary/', views.order_summary, name='order_summary'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('track-order/<str:order_id>/', views.track_order, name='track_order'),
    path('get-models/<int:brand_id>/', views.get_models, name='get_models'),

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve
import os

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.urls import path

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Serve static files in production (already handled by WhiteNoise, but safe to keep)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)




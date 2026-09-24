"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from store.views import *
from django.conf import settings
from django.conf.urls.static import static
from store import views
from . import *

urlpatterns = [
    path('', home_page, name='home_page'),
    path('', include('store.urls')),
    path('admin/', admin.site.urls),
    path('product/<slug:slug>/', product_detail, name='product_detail'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('buy/<int:pk>/', views.buy_now, name='buy_now'),
    path('about/', about_page, name='about_page'),
    path('accounts/', include('accounts.urls')),
    path('collection/<int:id>/', collection_page, name='collection_page'),
    path('blogs/', blog_list, name='blog_list'),
    path('blogs/<slug:slug>/', blog_detail, name='blog_detail'),
    path('faq/', faq_page, name='faq_page'),
    path('contact/', contact_page, name='contact_page'),
    path('success/', success_page, name='success_page'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path("cart/update/", views.update_cart, name="update_cart"),
    path('checkout/', checkout, name="checkout"),
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),

    path('checkout/', include('checkout.urls')),
    path('search/', search_products, name='search_products'),

    path('payment/', include('payments.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

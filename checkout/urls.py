from django.urls import path
from . import views
from .views import place_order

urlpatterns = [
    path('checkout/', views.checkout_page, name='checkout'),
    path('payment-method/', views.payment_method, name='payment_method'),
    path('payment-options/', views.payment_options, name='payment_options'),
    path('place-order/', place_order, name='place_order'),
]
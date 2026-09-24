from django.urls import path
from .views import home_page
from . import views

urlpatterns = [
    path('', home_page, name='home_page'),
]
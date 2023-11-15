# myapp/urls.py
from django.urls import path
from .views import shopify_webhook

urlpatterns = [
    
    path('shopify_webhook/', shopify_webhook, name='shopify_webhook'),
]

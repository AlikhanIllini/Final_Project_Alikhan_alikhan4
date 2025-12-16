"""
URL configuration for cards app.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Stock card management
    path('card/create/', views.card_create, name='card_create'),
    path('card/<int:card_id>/', views.card_detail, name='card_detail'),
    path('card/<int:card_id>/edit/', views.card_edit, name='card_edit'),
    path('card/<int:card_id>/delete/', views.card_delete, name='card_delete'),
    path('card/<int:card_id>/archive/', views.card_archive, name='card_archive'),

    # Price management
    path('card/<int:card_id>/refresh-price/', views.refresh_price, name='refresh_price'),
    path('card/<int:card_id>/manual-price/', views.manual_price, name='manual_price'),

    # Tag management
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/create/', views.tag_create, name='tag_create'),
    path('tags/<int:tag_id>/edit/', views.tag_edit, name='tag_edit'),
    path('tags/<int:tag_id>/delete/', views.tag_delete, name='tag_delete'),
]


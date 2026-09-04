from django.urls import path, re_path
from . import views

urlpatterns = [
    # General & Information Pages
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contacts/', views.contacts_view, name='contacts'),
    path('glossary/', views.glossary_view, name='glossary'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('faq/', views.faq_view, name='faq'),
    path('vacancies/', views.vacancies_view, name='vacancies'),
    path('promocodes/', views.promocodes_view, name='promocodes'),

    # Articles & News Feed
    path('news/', views.news_view, name='news'),
    path('news/create/', views.article_create_view, name='article_create'),
    path('news/<int:pk>/update/', views.article_update_view, name='article_update'),
    path('news/<int:pk>/delete/', views.article_delete_view, name='article_delete'),
    re_path(r'^news/(?P<pk>\d+)/$', views.article_detail_view, name='article_detail'),

    # User Reviews
    path('reviews/', views.reviews_view, name='reviews'),

    # Analytics & Statistics Charts
    path('statistics/', views.statistics_view, name='statistics'),

    # Authentication & User Dashboards
    path('register/', views.register_view, name='register'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Real Estate Properties CRUD & Detail Page
    path('properties/', views.property_list_view, name='property_list'),
    path('properties/add/', views.property_create_view, name='property_create'),
    re_path(r'^properties/(?P<pk>\d+)/$', views.property_detail_view, name='property_detail'),
    re_path(r'^properties/(?P<pk>\d+)/update/$', views.property_update_view, name='property_update'),
    re_path(r'^properties/(?P<pk>\d+)/delete/$', views.property_delete_view, name='property_delete'),

    # Cart & Checkout Logic (Корзина и Оплата)
    path('cart/', views.cart_view, name='cart_detail'),
    path('cart/add/<int:property_id>/', views.cart_add_view, name='cart_add'),
    path('cart/remove/<int:property_id>/', views.cart_remove_view, name='cart_remove'),
    path('cart/checkout/', views.checkout_view, name='checkout'),

    # Async API Endpoints
    path('api/v1/secured-stats/', views.secured_agency_stats_api, name='secured_agency_stats_api'),
    path('catalog/book/<int:property_id>/', views.create_deal_ajax, name='create_deal_ajax'),
]
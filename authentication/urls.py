# -*- encoding: utf-8 -*-
"""
Copyright (c) 2021 - Damilola x Technoserve
"""

from django.urls import path
from . import views
from .views import login_view, register_user, register_user_full, register_org, register_role, load_roles, profile, tables, activate, logout_view
from django.contrib.auth.views import LogoutView
from django.conf.urls import url

urlpatterns = [
    path('login/', login_view, name="login"),
    path('map/logout/', logout_view, name="logout"),
    path('map/register/', register_user, name="register"),
    path("map/logout/", LogoutView.as_view(), name="logout"),
    path("full_register/", register_user_full, name="full_register"),
    path("register_org/", register_org, name="register_org"),
    path("register_role/", register_role, name="register_role"),
    path('load_roles/', load_roles, name='load_roles'),
    path('map/profile/', profile, name='profile'),
    # path('tables/', tables, name='tables'),
    # url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', activate, name='activate'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('tables/', views.tables, name='tables'),
    path('map/plantations/', views.plantations, name='plantations'),
    path('map/yield/', views.yields, name='yield'),
    path('map/nurseries/', views.nurseries, name='nurseries'),
    path('map/shipment/', views.shipment, name='shipment'),
    path('map/drone/<plant_id>/<coordinate_xy>/', views.drone, name='drone'),
    # path('map/', views.index, name='map'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('password_reset_confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
]

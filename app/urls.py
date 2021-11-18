# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from app import views
from authentication import views as vw

urlpatterns = [

    # The home page
    path('map/', views.index, name='map'),
    path('', vw.login_view),
    
]


# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import path, include  # add this
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _

urlpatterns = [
    path(_('admin/'), admin.site.urls),          # Django admin route
]


urlpatterns += i18n_patterns (
    path("", include("authentication.urls")),
    path("", include("app.urls")),
    
)
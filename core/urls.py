# # -*- encoding: utf-8 -*-
# """
# Copyright (c) 2019 - present AppSeed.us
# """

# from django.contrib import admin
# from django.urls import path, include  # add this
# from django.conf.urls.i18n import i18n_patterns

# urlpatterns = [
#     path('admin/', admin.site.urls),          # Django admin route
#     path("", include("authentication.urls")), # Auth routes - login / register
#     path("", include("app.urls")),
#     path("", include("lang.urls", namespace='lang')),
# ]


# urlpatterns += i18n_patterns [
#     path("", include("lang.urls", namespace='lang')),
# ]
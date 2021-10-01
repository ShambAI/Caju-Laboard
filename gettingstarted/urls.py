from django.urls import path, include

from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
]

admin.autodiscover()

import hello.views

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    # path("", hello.views.home.as_view(), name="index"),
    path("admin/", admin.site.urls),
    path("", include("authentication.urls")), # Auth routes - login / register
    path("", include("app.urls"))             # UI Kits Html files
]

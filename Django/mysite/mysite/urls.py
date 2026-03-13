from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Polls Administration"
admin.site.site_title = "Polls Admin Portal"
admin.site.index_title = "Welcome to Polls Researcher Portal"

urlpatterns = [
    path("polls/", include("polls.urls")), # Має бути саме polls.urls
    path("admin/", admin.site.urls),
]
from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("tags/<slug:tag_slug>/", views.PostList.as_view(), name="post_list_tag"),
    path("", views.PostList.as_view(), name="post_list"),
    path("<slug:slug>/", views.post_detail, name="post_detail"),
    path("share/<int:post_id>/", views.post_share, name="post_share"),
]

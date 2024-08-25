from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from tendering.models import Comment
from tendering.views import (
    index,
    InactiveLotListView,
    ActiveLotListView,
    UserListView,
    UserDetailView,
    LotDetailView,
    CommentCreateView
)


urlpatterns = [
    path("", index, name="index"),
    path("inactive_lots/", InactiveLotListView.as_view(), name="lot-list"),
    path("active_lots/", ActiveLotListView.as_view(), name="lot-list"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("lots/<int:pk>/", LotDetailView.as_view(), name="lot-detail"),
    path("lots/<int:pk>/comment/", CommentCreateView.as_view(), name="comment-create"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


app_name = "tendering"


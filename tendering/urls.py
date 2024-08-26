from django.conf import settings
from django.conf.urls.static import static
from django.urls import path


from tendering.views import (
    index,
    InactiveLotListView,
    ActiveLotListView,
    UserListView,
    UserDetailView,
    LotDetailView,
    CommentCreateView,
    BidCreateView,
    LotCreateView,
    LotUpdateView,
    LotDeleteView,
)


urlpatterns = [
    path("", index, name="index"),
    path("inactive_lots/", ActiveLotListView.as_view(), name="lot-list-active"),
    path("active_lots/", InactiveLotListView.as_view(), name="lot-list-inactive"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("lots/<int:pk>/", LotDetailView.as_view(), name="lot-detail"),
    path("lots/<int:pk>/comment/", CommentCreateView.as_view(), name="comment-create"),
    path("lots/<int:pk>/bid/", BidCreateView.as_view(), name="bid-create"),
    path("lots/create/", LotCreateView.as_view(), name="lot-create"),
    path("lots/<int:pk>/update/", LotUpdateView.as_view(), name="lot-update"),
    path("lots/<int:pk>/delete/", LotDeleteView.as_view(), name="lot-delete"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


app_name = "tendering"


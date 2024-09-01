from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from admin_soft import views as soft_views
from tendering.views import (
    index,
    register,
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
    UserCreateView,
    UserUpdateView,
    UserDeleteView,
)


urlpatterns = [
    path("", index, name="index"),
    path("active_lots/", ActiveLotListView.as_view(), name="lot-list-active"),
    path("inactive_lots/", InactiveLotListView.as_view(), name="lot-list-inactive"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("users/<int:pk>/update/", UserUpdateView.as_view(), name="user-update"),
    path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="user-delete"),
    path("users/create/", UserCreateView.as_view(), name="user-create"),
    path("lots/<int:pk>/", LotDetailView.as_view(), name="lot-detail"),
    path("lots/<int:pk>/comment/", CommentCreateView.as_view(), name="comment-create"),
    path("lots/<int:pk>/bid/", BidCreateView.as_view(), name="bid-create"),
    path("lots/create/", LotCreateView.as_view(), name="lot-create"),
    path("lots/<int:pk>/update/", LotUpdateView.as_view(), name="lot-update"),
    path("lots/<int:pk>/delete/", LotDeleteView.as_view(), name="lot-delete"),
    path("accounts/register/", register, name="register"),
    path("accounts/logout/", soft_views.logout_view, name="logout"),
    path("accounts/login/", soft_views.UserLoginView.as_view(), name="login"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


app_name = "tendering"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

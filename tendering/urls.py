from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from tendering.views import (
    index,
    InactiveLotListView,
    ActiveLotListView,
)


urlpatterns = [
    path("", index, name="index"),
    path("inactive_lots/", InactiveLotListView.as_view(), name="lot-list"),
    path("active_lots/", ActiveLotListView.as_view(), name="lot-list"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


app_name = "tendering"


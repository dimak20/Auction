from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from tendering.views import index


urlpatterns = [
    path("", index, name="index")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


app_name = "tendering"


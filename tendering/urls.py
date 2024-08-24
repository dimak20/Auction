from django.conf import settings
from django.conf.urls.static import static
from django.urls import path



urlpatterns = [
    path("", index, name="index")
]


app_name = "tendering"

